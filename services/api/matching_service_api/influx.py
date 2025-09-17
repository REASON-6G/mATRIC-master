from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from influxdb_client import InfluxDBClient

from matching_service_api.config import Config

influx_bp = Blueprint("influx", __name__, url_prefix="/influx")

# Config from env
INFLUX_URL = Config.INFLUX_URL
INFLUX_TOKEN = Config.INFLUX_TOKEN
INFLUX_ORG = Config.INFLUX_ORG
INFLUX_BUCKET = Config.INFLUX_BUCKET

client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)

@influx_bp.route("/query", methods=["POST"])
@jwt_required()
def query():
    body = request.get_json() or {}
    flux = body.get("flux")
    if not flux:
        return jsonify({"msg": "flux query required"}), 400

    query_api = client.query_api()
    try:
        result = query_api.query(flux)
        rows = []
        for table in result:
            for record in table.records:
                rows.append({
                    "time": record.get_time().isoformat(),
                    "measurement": record.get_measurement(),
                    "field": record.get_field(),
                    "value": record.get_value(),
                    "tags": record.values
                })
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@influx_bp.route("/write", methods=["POST"])
@jwt_required()
def write():
    body = request.get_json() or {}
    data = body.get("data")
    if not data:
        return jsonify({"msg": "data required"}), 400

    write_api = client.write_api()
    try:
        write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=data)
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
