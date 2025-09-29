# app/rabbitmq/subscriber_emulator_linux.py
import json
import logging
import os
import shutil
import subprocess
from typing import Any, Dict, List, Optional

from app.rabbitmq.consumer import RabbitMQConsumer
from app.database import mark_agents_started  # stamps emulator_started_at for agents

# Optional override via env:
ANSIBLE_PLAYBOOK_CMD = os.getenv("ANSIBLE_PLAYBOOK_CMD", "ansible-playbook")


def _resolve_playbooks_dir(logger: logging.Logger) -> str:
    """
    Try several locations so the code works both in dev and inside the container.
    Order:
      1) PLAYBOOKS_DIR env
      2) /app/app/playbooks        (typical for this project layout in the container)
      3) /app/playbooks            (previous default)
      4) <this_file_dir>/../playbooks
    Returns the first dir that exists; if none exist, returns the first candidate
    so error messages are predictable.
    """
    env_dir = os.getenv("PLAYBOOKS_DIR")
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        env_dir,
        "/app/app/playbooks",
        "/app/playbooks",
        os.path.abspath(os.path.join(here, "..", "playbooks")),
    ]
    candidates = [c for c in candidates if c]  # drop None

    for d in candidates:
        if os.path.isdir(d):
            logger.info("Using playbooks directory: %s", d)
            return d

    logger.warning(
        "None of the expected playbooks directories exist. Candidates were: %s. "
        "Proceeding with first candidate for clear errors.",
        candidates,
    )
    return candidates[0]


class EmulatorTaskSubscriberLinux:
    """
    Consumes messages from 'emulator_spinup', runs Ansible playbooks, and
    on success calls mark_agents_started(agents) to stamp emulator_started_at.

    Expected message:
    {
      "job_number": "...",
      "emulators": [
        {
          "access_point_type": "WiFi" | "5G" | "LiFi",
          "num_access_points": 2,
          "locations": [...],
          "num_devices": 10,
          "duration": 30,
          "agents": [ {"ap_id": "...", "password": "...", "location": {...}}, ... ]
        },
        ...
      ]
    }
    """

    def __init__(self, queue_name: str = "emulator_spinup"):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.queue_name = queue_name
        self.consumer = RabbitMQConsumer(queue_name=self.queue_name)

        # Resolve ansible binary now for clearer logs
        resolved = shutil.which(ANSIBLE_PLAYBOOK_CMD)
        if not resolved:
            self.logger.warning(
                "Could not find '%s' on PATH. Install Ansible in this container "
                "or set ANSIBLE_PLAYBOOK_CMD to the full path.",
                ANSIBLE_PLAYBOOK_CMD,
            )
        self.ansible_bin = resolved or ANSIBLE_PLAYBOOK_CMD

        # Resolve playbooks directory
        self.playbooks_dir = _resolve_playbooks_dir(self.logger)

    # ---------- helpers ----------

    @staticmethod
    def _playbook_for(ap_type: str) -> str:
        mapping = {
            "5G": "spinup_5g.yml",
            "WiFi": "spinup_wifi.yml",
            "LiFi": "spinup_lifi.yml",
        }
        if ap_type not in mapping:
            raise ValueError(f"Unsupported access point type: {ap_type}")
        return mapping[ap_type]

    def _run_playbook(self, playbook_filename: str, extra_vars: Dict[str, Any]) -> subprocess.CompletedProcess:
        playbook_path = os.path.join(self.playbooks_dir, playbook_filename)
        if not os.path.isfile(playbook_path):
            raise FileNotFoundError(f"Playbook not found: {playbook_path}")

        # Use in-memory localhost inventory and local connection to avoid inventory warnings.
        cmd = [
            self.ansible_bin,
            "-i", "localhost,",
            "-c", "local",
            "-e", "ansible_python_interpreter=/usr/bin/python3",
            playbook_path,
            "--extra-vars",
            json.dumps(extra_vars),
        ]
        self.logger.info("Running: %s", " ".join(cmd))
        return subprocess.run(cmd, capture_output=True, text=True)

    # ---------- consumer callback (single-arg!) ----------

    def on_message(self, payload: Any) -> None:
        try:
            if not isinstance(payload, dict):
                payload = json.loads(payload.decode("utf-8") if isinstance(payload, (bytes, bytearray)) else payload)

            self.logger.info("Received message: %s", payload)

            job_number: Optional[str] = payload.get("job_number")
            emulators: List[Dict[str, Any]] = payload.get("emulators", [])

            for emu in emulators:
                ap_type = emu.get("access_point_type")
                extra_vars = {
                    "job_number": job_number,
                    "access_point_type": ap_type,
                    "num_access_points": emu.get("num_access_points"),
                    "locations": emu.get("locations"),
                    "num_devices": emu.get("num_devices"),
                    "duration": emu.get("duration"),
                    "agents": emu.get("agents", []),
                }

                self.logger.info(
                    "Processing job %s for %s (num_access_points=%s num_devices=%s duration=%s)",
                    job_number,
                    ap_type,
                    extra_vars["num_access_points"],
                    extra_vars["num_devices"],
                    extra_vars["duration"],
                )

                playbook = self._playbook_for(ap_type)

                try:
                    result = self._run_playbook(playbook, extra_vars)
                except FileNotFoundError as fnf:
                    self.logger.error("Playbook invocation failed: %s", fnf)
                    continue
                except Exception as e:
                    self.logger.exception("Unexpected error running playbook: %s", e)
                    continue

                if result.returncode == 0:
                    updated = mark_agents_started(extra_vars["agents"])
                    self.logger.info(
                        "Playbook succeeded for job %s (%s); updated %d agent(s).",
                        job_number,
                        ap_type,
                        updated,
                    )
                else:
                    stdout_tail = (result.stdout or "")[-4000:]
                    stderr_tail = (result.stderr or "")[-4000:]
                    self.logger.error(
                        "Playbook failed for job %s (%s). RC=%s\nSTDOUT (tail):\n%s\nSTDERR (tail):\n%s",
                        job_number,
                        ap_type,
                        result.returncode,
                        stdout_tail,
                        stderr_tail,
                    )

        except Exception as e:
            self.logger.exception("Error processing message: %s", e)

    # ---------- runner ----------

    def run(self):
        self.logger.info("Starting EmulatorTaskSubscriberLinux on queue '%s'…", self.queue_name)
        self.consumer.consume(self.on_message)


if __name__ == "__main__":
    EmulatorTaskSubscriberLinux().run()
