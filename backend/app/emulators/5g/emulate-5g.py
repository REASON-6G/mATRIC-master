#!/usr/bin/env python3
# app/emulators/5g/emulate-5g.py
"""
5G AP Emulator

- Auth with agent creds (password grant) to backend.
- Every 5s, generate a 5G payload and POST:
    {
      "ap_id": "<AP>",
      "payload": { ... 5G fields ... }
    }
  to /api/v1/agent_update/update.

Includes VERBOSE logging:
- Prints TOKEN_URL / POST_URL at startup
- For each tick: logs POST URL, first 500 chars of body, HTTP status, and JSON/text response (truncated)
"""

import argparse
import json
import os
import random
import string
import sys
import time
from datetime import datetime, timedelta

import requests

# Defaults (can be overridden by CLI or env)
TOKEN_URL = os.getenv("TOKEN_URL", "http://backend/api/v1/token/?login_type=agent")
POST_URL  = os.getenv("POST_URL",  "http://backend/api/v1/agent_update/update")

PUBLISH_INTERVAL   = 5   # seconds
REFRESH_THRESHOLD  = 30  # seconds remaining → refresh/re-login


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
        "refresh_token": tok.get("refresh_token"),  # may be None
    }


def _ensure_token(tokens: dict, ap_id: str, password: str, token_url: str) -> dict:
    if not tokens:
        return _get_token(ap_id, password, token_url)
    if (tokens["expires_at"] - datetime.utcnow()).total_seconds() <= REFRESH_THRESHOLD:
        # Try refresh if we have a refresh_token; otherwise re-login
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


# ---------- PAYLOAD ----------
def _random_time() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def build_5g_payload(ap_id: str, lat: float, lon: float, devices: int) -> dict:
    return {
        "Aptech": "5G",
        "Latitude": lat,
        "Longitude": lon,
        "distName": "dist_" + "".join(random.choices(string.ascii_letters, k=5)),
        "cellId": "".join(random.choices(string.ascii_letters + string.digits, k=8)),
        "cellType": random.randint(1, 4),
        "apId": ap_id,
        "deviceCount": devices,
        "actualStartTime": _random_time(),
        "actualStopTime": _random_time(),
        "fwdTestDisp": "fwd_" + "".join(random.choices(string.ascii_letters, k=3)),
        "result": "result_" + "".join(random.choices(string.ascii_letters, k=3)),
        "ant1": random.randint(1, 100),
        "ant2": random.randint(1, 100),
        "ant3": random.randint(1, 100),
        "ant4": random.randint(1, 100),
    }


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

        payload = build_5g_payload(ap_id, lat, lon, devices)
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
    parser = argparse.ArgumentParser(description="5G AP Emulator")
    parser.add_argument("--ap-id", required=True, help="Agent/AP ID (username)")
    parser.add_argument("--password", required=True, help="Agent password")
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
