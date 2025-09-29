# backend/app/routes/emulator.py
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Tuple, Dict, Any
import os
import uuid
import re
import requests

from app.auth import get_authenticated_user_or_app, auth_manager
from app.database import DatabaseManager, get_db_manager
from app.rabbitmq.rabbitmq_publisher import RabbitMQPublisher
from app.models import EmulatorSpinupRequest

router = APIRouter()
publisher = RabbitMQPublisher()

# ---------- Helpers ----------

_MAPBOX_GEOCODE_URL = "https://api.mapbox.com/geocoding/v5/mapbox.places/{q}.json"

def _slugify_name(s: str) -> str:
    s = re.sub(r"[^A-Za-z0-9]+", "-", s.strip())
    return re.sub(r"-+", "-", s).strip("-")[:30] or "Loc"

def _short_id() -> str:
    return uuid.uuid4().hex[:4].upper()

def geocode_place(name_or_pair: str) -> Tuple[float, float, str]:
    """
    Accepts either:
      - place name (e.g. 'Leeds', 'London') -> geocode via Mapbox
      - 'lat,lon' string -> parsed directly
    Returns: (lat, lon, normalised_label)
    """
    # Try direct "lat,lon"
    m = re.match(r"^\s*(-?\d+(\.\d+)?)\s*,\s*(-?\d+(\.\d+)?)\s*$", name_or_pair)
    if m:
        lat = float(m.group(1))
        lon = float(m.group(3))
        return (lat, lon, f"{lat:.5f},{lon:.5f}")

    token = os.getenv("MAPBOX_TOKEN") or os.getenv("VITE_MAPBOX_TOKEN") or os.getenv("MAPBOX_ACCESS_TOKEN")
    if not token:
        raise HTTPException(status_code=400, detail="Geocoding requires MAPBOX token (MAPBOX_TOKEN / VITE_MAPBOX_TOKEN).")

    url = _MAPBOX_GEOCODE_URL.format(q=requests.utils.quote(name_or_pair))
    params = {"access_token": token, "limit": 1}
    try:
        resp = requests.get(url, params=params, timeout=8)
        resp.raise_for_status()
        data = resp.json()
        features = data.get("features") or []
        if not features:
            raise HTTPException(status_code=400, detail=f"Location not found: {name_or_pair}")
        f0 = features[0]
        lon, lat = f0["center"]
        label = f0.get("place_name") or name_or_pair
        return (float(lat), float(lon), label)
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Geocoding error: {e}")

# ---------- Route ----------

@router.post("/spinup")
async def spinup_emulators(
    payload: EmulatorSpinupRequest,
    _: Any = Depends(get_authenticated_user_or_app),
    dbm: DatabaseManager = Depends(get_db_manager),
):
    """
    - Auth required (user or app).
    - Creates emulator agents using DatabaseManager.add_agent with hashed passwords.
    - Normalises locations to lat/lon and stores them ONLY in agent.configuration.geolocation.
    - Publishes a job to RabbitMQ (routing key: emulator_spinup) including agent creds and locations.
    """
    job_number = str(uuid.uuid4())

    # Outgoing message for the subscriber/Ansible
    message: Dict[str, Any] = {"job_number": job_number, "emulators": []}
    created_agents_summary: List[Dict[str, Any]] = []

    for emu in payload.emulators:
        # Normalise locations to coordinates
        normalised_locations: List[Dict[str, Any]] = []
        for loc in emu.locations:
            lat, lon, label = geocode_place(loc)
            normalised_locations.append({"name": label, "lat": lat, "lon": lon})

        # Create emulator agents (one per requested AP), cycle locations if needed
        agents_for_emulator: List[Dict[str, Any]] = []
        for i in range(emu.num_access_points):
            loc = normalised_locations[i % len(normalised_locations)]
            base_name = _slugify_name(loc["name"])
            ap_id = f"Emu-{base_name}-{_short_id()}"
            password_plain = uuid.uuid4().hex  # random strong secret
            password_hash = auth_manager.hash_password(password_plain)

            configuration = {
                "geolocation": {"lat": str(loc["lat"]), "lon": str(loc["lon"])},
                "access_point_type": emu.access_point_type,
                "job_number": job_number,
                "emulator": True,
                "num_devices": emu.num_devices,
                "duration": emu.duration,
            }

            # Use DB manager to create the agent
            dbm.add_agent(ap_id=ap_id, password_hash=password_hash, configuration=configuration)

            # Location + creds sent to the task message (for Ansible/emulator)
            agents_for_emulator.append(
                {
                    "ap_id": ap_id,
                    "password": password_plain,
                    "location": {"lat": loc["lat"], "lon": loc["lon"], "name": loc["name"]},
                }
            )

            created_agents_summary.append({"ap_id": ap_id, "access_point_type": emu.access_point_type})

        message["emulators"].append(
            {
                "access_point_type": emu.access_point_type,
                "num_access_points": emu.num_access_points,
                "locations": normalised_locations,  # for Ansible/emulator
                "num_devices": emu.num_devices,
                "duration": emu.duration,
                "agents": agents_for_emulator,      # includes ap_id + password + per agent location
            }
        )

    # Publish to RabbitMQ
    try:
        publisher.publish(routing_key="emulator_spinup", message=message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to publish task: {e}")

    return {"status": "queued", "job_number": job_number, "agents": created_agents_summary}
