from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Iterable, Optional, List

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session

# Project imports
from app.dependencies import get_db
from app.auth import get_current_user, TokenData
from app.models import Agents  # SQLAlchemy Agents model
from app.utils.influxdb_reader import InfluxDBReader

router = APIRouter()


# ---------------- Helper functions ----------------

def _minutes_or_flux_to_minutes(window: str | int) -> int:
    """
    Convert common window inputs to minutes:
    - int -> minutes
    - '5m' -> 5
    - '1h' -> 60
    - '30s' -> 1 (floored to 1 minute)
    """
    if isinstance(window, int):
        return max(1, window)
    s = str(window).strip().lower()
    try:
        if s.endswith("m"):
            return max(1, int(s[:-1] or "1"))
        if s.endswith("h"):
            return max(1, int(s[:-1] or "1") * 60)
        if s.endswith("s"):
            return 1
        return max(1, int(s))
    except Exception:
        return 5


def _to_rfc3339z(dt: datetime) -> str:
    """
    Convert a timezone aware datetime to RFC3339 with 'Z' (Flux friendly).
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _normalise_points_from_influx(records: Iterable[dict[str, Any]]) -> List[dict]:
    """
    Keep the original 'field' from Influx, plus timestamp and value.
    Output shape per point:
      { "ts": "<ISO>", "value": <float>, "key": "<field name>" }
    """
    pts: list[dict] = []
    for rec in records or []:
        t = rec.get("time")
        v = rec.get("value")
        k = rec.get("field")  # this is the key name from payload
        if t is None or v is None:
            continue
        ts = t.isoformat() if hasattr(t, "isoformat") else str(t)
        try:
            val = float(v)
        except (TypeError, ValueError):
            continue
        pts.append({"ts": ts, "value": val, "key": k})
    return pts


def _get_agent_data_via_reader(ap_id: str, start: datetime, stop: datetime) -> List[dict]:
    """
    InfluxDBReader.query_agent_data(agent_id: str, start_time: str, end_time: str)
    Times are sent as RFC3339 with 'Z'.
    """
    reader = InfluxDBReader()
    try:
        data = reader.query_agent_data(
            agent_id=ap_id,
            start_time=_to_rfc3339z(start),
            end_time=_to_rfc3339z(stop),
        )
        return _normalise_points_from_influx(data)
    finally:
        try:
            reader.close()
        except Exception:
            pass


# ---------------- Endpoints ----------------

@router.get("/agent_details")
def agent_details(
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """
    Return agents directly from the database with these fields:
    id, ap_id, configuration, onboard.

    """
    try:
        rows: list[Agents] = db.query(Agents).all()
        return [
            {
                "id": str(row.id),
                "ap_id": row.ap_id,
                "configuration": row.configuration or {},
                "onboard": bool(row.onboard),
            }
            for row in rows
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"agent_details failed: {e}") from e


@router.get("/agent_data")
def get_agent_data(
    agent: str = Query(..., description="Agent ap_id (exact value used in Influx measurement 'agent/<ap_id>/data')"),
    window: str | int = Query(5, description="Window size, for example 1, 5, 10 (minutes) or '1h'"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """
    Pull time series for one agent using your exact InfluxDB reader (JWT required).
    Works only with the agent's ap_id. Returns the key from Influx as 'key'.
    """
    try:
        win_min = _minutes_or_flux_to_minutes(window)
        stop = datetime.now(timezone.utc)
        start = stop - timedelta(minutes=win_min)

        points = _get_agent_data_via_reader(ap_id=agent, start=start, stop=stop)
        return {"agent_id": agent, "points": points}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"agent_data failed: {e}") from e
