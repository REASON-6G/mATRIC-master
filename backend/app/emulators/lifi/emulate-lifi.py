#!/usr/bin/env python3
# backend/app/emulators/lifi/emulate-lifi.py
"""
LiFi AP Emulator

Interface is identical to 5G/WiFi:
- Auth with agent creds (password grant) to backend.
- Every 5s, generate a LiFi payload and POST:
    {
      "ap_id": "<AP>",
      "payload": { ... fields ... }
    }
  to /api/v1/agent_update/update.

Verbose logging:
- Prints TOKEN_URL / POST_URL at startup
- Each tick logs POST url, first 500 chars of the body, HTTP status, and response.
"""

import argparse
import json
import os
import random
import string
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, List

import requests

# Defaults (can be overridden by CLI or env)
TOKEN_URL = os.getenv("TOKEN_URL", "http://backend/api/v1/token/?login_type=agent")
POST_URL  = os.getenv("POST_URL",  "http://backend/api/v1/agent_update/update")

PUBLISH_INTERVAL   = 5   # seconds
REFRESH_THRESHOLD  = 30  # seconds remaining → refresh/re-login
MAX_STATIONS       = 32  # how many flat stationN fields we include


def _log(msg: str) -> None:
    print(f"[{datetime.utcnow().isoformat()}Z] {msg}", flush=True)


def _should_post(url: str) -> bool:
    if not url:
        return False
    u = str(url).strip().strip("\"'").lower()
    return bool(u) and u not in ("none", "null", "false")


# ---------- AUTH ----------
def _get_token(ap_id: str, password: str, token_url: str) -> dict:
    data = {"username": ap_id, "password": password, "grant_type": "password"}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    resp = requests.post(token_url, data=data, headers=headers, timeout=10)
    resp.raise_for_status()
    tok = resp.json()

    access = tok.get("access_token")
    if not access:
        raise RuntimeError(f"Token missing access_token: {tok}")
    expires_in = int(tok.get("expires_in", 3600))

    return {
        "access_token": access,
        "expires_at": datetime.utcnow() + timedelta(seconds=expires_in),
        "token_type": tok.get("token_type", "bearer"),
        "refresh_token": tok.get("refresh_token"),
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
                access = tok.get("access_token")
                if access:
                    expires_in = int(tok.get("expires_in", 3600))
                    tokens = {
                        "access_token": access,
                        "token_type": tok.get("token_type", "bearer"),
                        "refresh_token": tok.get("refresh_token", tokens["refresh_token"]),
                        "expires_at": datetime.utcnow() + timedelta(seconds=expires_in),
                    }
                    return tokens
            except Exception:
                # fall back to re-login
                pass
        return _get_token(ap_id, password, token_url)
    return tokens


# ---------- HELPERS ----------
def _rand_mac() -> str:
    return ":".join("".join(random.choices("0123456789abcdef", k=2)) for _ in range(6))


def _stations_flat(n: int) -> Dict[str, str]:
    n = max(0, min(n, MAX_STATIONS))
    base = [
        "f4:7b:09:f0:9d:f3",
        "c8:3a:35:a4:06:9d",
        "a9:a1:bb:9f:e2:12",
    ]
    while len(base) < n:
        base.append(_rand_mac())
    base = base[:n]
    return {f"station{i+1}": mac for i, mac in enumerate(base)}


def _random_time() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


# ---------- PAYLOAD ----------
def build_lifi_payload(ap_id: str, lat: float, lon: float, devices: int) -> dict:
    """
    Simple LiFi payload; mirror WiFi/5G structure.
    Includes some LiFi-flavoured fields (wavelength/power/snr/modulation).
    """
    payload = {
        "Aptech": "LiFi",
        "apId": ap_id,
        "Latitude": lat,
        "Longitude": lon,
        "deviceCount": devices,
        "ts": _random_time(),
        # LiFi-ish parameters (purely synthetic)
        "wavelength_nm": random.choice([450, 520, 630, 660]),  # example wavelengths
        "optical_power_dbm": round(random.uniform(-25.0, 0.0), 2),
        "snr_db": round(random.uniform(5.0, 40.0), 1),
        "modulation": random.choice(["OOK", "VPPM", "CSK", "OFDM"]),
        "luminaire_id": "lum_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=6)),
        "room": random.choice(["lab-1", "office-2", "hall-3", "demo-4"]),
    }
    # Flattened station list: station1..stationN = MAC
    payload.update(_stations_flat(min(devices, MAX_STATIONS)))
    return payload


# ---------- MAIN LOOP ----------
def run(ap_id: str, password: str, lat: float, lon: float, devices: int,
        duration_minutes: int, token_url: str, post_url: str) -> None:
    _log(f"TOKEN_URL: {token_url}")
    _log(f"POST_URL:  {post_url}")

    # auth
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

        payload = build_lifi_payload(ap_id, lat, lon, devices)
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
    parser = argparse.ArgumentParser(description="LiFi AP Emulator")
    parser.add_argument("--ap-id", required=True, help="Agent/AP ID (username)")
    # allow password via flag or ENV (EMU_PASSWORD)
    env_pwd = os.getenv("EMU_PASSWORD")
    parser.add_argument("--password", required=(env_pwd is None), default=env_pwd, help="Agent password")
    parser.add_argument("--lat", required=True, type=float)
    parser.add_argument("--lon", required=True, type=float)
    parser.add_argument("--devices", type=int, default=1)
    parser.add_argument("--duration-minutes", type=int, required=True)
    parser.add_argument("--token-url", default=TOKEN_URL)
    parser.add_argument("--post-url", default=POST_URL)
    args = parser.parse_args()

    # normalize URLs
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
