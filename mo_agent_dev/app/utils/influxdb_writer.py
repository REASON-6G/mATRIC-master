# utils/influxdb_writer.py

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from app.config import settings
from datetime import datetime
import logging

class InfluxDBWriter:
    def __init__(self):
        """Initialize the InfluxDB client and write API."""
        self.client = InfluxDBClient(
            url=settings.influxdb_config["influx_url"],
            token=settings.influxdb_config["influx_token"],
            org=settings.influxdb_config["influx_org"]
        )
        self.bucket = settings.influxdb_config["influx_bucket"]
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)

    def write_data(self, measurement: str, data: dict):
        """Write data to InfluxDB with dynamic fields."""
        try:
            # Create a point with a dynamic measurement
            point = Point(measurement).tag("source", "agent").time(datetime.utcnow())
            for key, value in data.items():
                point = point.field(key, value)
            
            # Write the point to the specified bucket
            self.write_api.write(bucket=self.bucket, record=point)
            logging.info(f"Data written to InfluxDB: {data}")
        except Exception as e:
            logging.error(f"Failed to write data to InfluxDB: {e}")

    def close(self):
        """Close the InfluxDB client connection."""
        self.client.close()
        logging.info("InfluxDB client closed")
