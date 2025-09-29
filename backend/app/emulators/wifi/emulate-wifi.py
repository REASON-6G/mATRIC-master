#!/usr/bin/env python3
# backend/app/emulators/wifi/emulate-wifi.py
"""
WiFi AP Emulator

- Auth with agent creds (password grant) to backend.
- Every 5s, generate a WiFi payload and POST:
    {
      "ap_id": "<AP>",
      "payload": {
         "Aptech": "WiFi",
         ...,
         "station1": "<MAC>",
         "station2": "<MAC>",
         ...
      }
    }
  to /api/v1/agent_update/update

Env/CLI compatible with 5G emulator:
- TOKEN_URL (default: http://backend/api/v1/token/?login_type=agent)
- POST_URL  (default: http://backend/api/v1/agent_update/update)

CLI:
  --ap-id, --password, --lat, --lon, --devices, --duration-minutes,
  --token-url, --post-url
"""

import argparse
import json
import os
import random
import string
import sys
import time
from datetime import datetime, timedelta
from typing import List

import requests

TOKEN_URL = os.getenv("TOKEN_URL", "http://backend/api/v1/token/?login_type=agent")
POST_URL  = os.getenv("POST_URL",  "http://backend/api/v1/agent_update/update")

PUBLISH_INTERVAL  = 5   # seconds
REFRESH_THRESHOLD = 30  # seconds left -> refresh/re-login


def _log(msg: str) -> None:
    print(f"[{datetime.utcnow().isoformat()}Z] {msg}", flush=True)


def _should_post(url: str) -> bool:
    if not url:
        return False
    u = str(url).strip().strip("\"'")
    return bool(u) and u.lower() not in ("none", "null", "false")


# ---------- AUTH ----------
def _get_token(ap_id: str, password: str, token_url: str) -> dict:
    data = {"username": ap_id, "password": password, "grant_type": "password"}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    r = requests.post(token_url, data=data, headers=headers, timeout=10)
    r.raise_for_status()
    tok = r.json()

    access = tok.get("access_token")
    if not access:
        raise RuntimeError(f"Token missing access_token: {tok}")
    expires_in = int(tok.get("expires_in", 3600))
    return {
        "access_token": access,
        "token_type": tok.get("token_type", "bearer"),
        "refresh_token": tok.get("refresh_token"),
        "expires_at": datetime.utcnow() + timedelta(seconds=expires_in),
    }


def _ensure_token(tokens: dict, ap_id: str, password: str, token_url: str) -> dict:
    if not tokens:
        return _get_token(ap_id, password, token_url)
    if (tokens["expires_at"] - datetime.utcnow()).total_seconds() <= REFRESH_THRESHOLD:
        if tokens.get("refresh_token"):
            try:
                data = {"grant_type": "refresh_token", "refresh_token": tokens["refresh_token"]}
                headers = {"Content-Type": "application/x-www-form-urlencoded"}
                r = requests.post(token_url, data=data, headers=headers, timeout=10)
                r.raise_for_status()
                tok = r.json()
                acc = tok.get("access_token")
                if acc:
                    expires_in = int(tok.get("expires_in", 3600))
                    return {
                        "access_token": acc,
                        "token_type": tok.get("token_type", "bearer"),
                        "refresh_token": tok.get("refresh_token", tokens["refresh_token"]),
                        "expires_at": datetime.utcnow() + timedelta(seconds=expires_in),
                    }
            except Exception:
                pass
        return _get_token(ap_id, password, token_url)
    return tokens


# ---------- WiFi payload (MACs flattened as station1, station2, …) ----------
_STATIONS = [
    "f4:7b:09:f0:9d:f3",
    "c8:3a:35:a4:06:9d",
    "a9:a1:bb:9f:e2:12",
    "34:ab:95:0f:72:5d",
    "5c:ad:cf:1b:44:8a",
]

def _ri(a: int, b: int) -> int:
    return random.randint(a, b)

def _random_mac() -> str:
    return ":".join("".join(random.choices("0123456789abcdef", k=2)) for _ in range(6))

def _pick_macs(devices: int) -> List[str]:
    """Return exactly `devices` MAC addresses."""
    if devices <= len(_STATIONS):
        return random.sample(_STATIONS, k=max(1, devices))
    # need more -> extend with synthetic MACs
    macs = list(_STATIONS)
    while len(macs) < devices:
        macs.append(_random_mac())
    return macs[:devices]

def build_wifi_payload(ap_id: str, lat: float, lon: float, devices: int) -> dict:
    macs: List[str] = _pick_macs(max(1, devices))

    # Flatten into station1..stationN : "<MAC>"
    stations_flat = {f"station{i+1}": mac for i, mac in enumerate(macs)}

    payload = {
        "Aptech": "WiFi",
        "apId": ap_id,
        "Latitude": lat,
        "Longitude": lon,
        "deviceCount": len(macs),
        "ssid": "matric-" + "".join(random.choices(string.ascii_lowercase, k=4)),
        "bssid": _random_mac(),
        "channel": _ri(1, 165),
        "band": random.choice(["2.4GHz", "5GHz", "6GHz"]),
        "ts": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    }
    payload.update(stations_flat)
    return payload


# ---------- MAIN ----------
def run(ap_id: str, password: str, lat: float, lon: float, devices: int,
        duration_minutes: int, token_url: str, post_url: str) -> None:
    _log(f"TOKEN_URL: {token_url}")
    _log(f"POST_URL:  {post_url}")

    try:
        tokens = _get_token(ap_id, password, token_url)
    except Exception as e:
        _log(f"FATAL: {e}")
        sys.exit(1)
    _log("Authenticated.")

    deadline = datetime.utcnow() + timedelta(minutes=duration_minutes)

    while datetime.utcnow() < deadline:
        tokens = _ensure_token(tokens, ap_id, password, token_url)
        headers = {
            "Authorization": f"Bearer {tokens['access_token']}",
            "Content-Type": "application/json",
        }

        payload = build_wifi_payload(ap_id, lat, lon, devices)
        body = {"ap_id": ap_id, "payload": payload}

        _log("tick: payload built")

        if _should_post(post_url):
            try:
                body_str = json.dumps(body, ensure_ascii=False)
                _log(f"POST -> {post_url}")
                _log(f"POST body (first 500): {body_str[:500]}")
                r = requests.post(post_url, json=body, headers=headers, timeout=10)
                _log(f"POST <- {r.status_code} {r.reason}")
                ct = (r.headers.get("content-type") or "").lower()
                if "json" in ct:
                    try:
                        _log(f"POST resp.json: {r.json()}")
                    except Exception:
                        _log(f"POST resp.text (first 500): {r.text[:500]}")
                else:
                    _log(f"POST resp.text (first 500): {r.text[:500]}")
                r.raise_for_status()
            except Exception as e:
                _log(f"POST error: {e}")

        time.sleep(PUBLISH_INTERVAL)

    _log("Emulation completed.")


def main():
    parser = argparse.ArgumentParser(description="WiFi AP Emulator")
    parser.add_argument("--ap-id", required=True, help="Agent/AP ID (username)")
    parser.add_argument("--password", required=True, help="Agent password")
    parser.add_argument("--lat", required=True, type=float)
    parser.add_argument("--lon", required=True, type=float)
    parser.add_argument("--devices", type=int, default=1)
    parser.add_argument("--duration-minutes", type=int, required=True)
    parser.add_argument("--token-url", default=TOKEN_URL)
    parser.add_argument("--post-url", default=POST_URL)
    args = parser.parse_args()

    token_url = (args.token_url or TOKEN_URL).strip()
    post_url  = (args.post_url  or POST_URL).strip()

    run(
        ap_id=args.ap_id,
        password=args.password,
        lat=args.lat,
        lon=args.lon,
        devices=args.devices,
        duration_minutes=args.duration_minutes,
        token_url=token_url,
        post_url=post_url,
    )


if __name__ == "__main__":
    main()
