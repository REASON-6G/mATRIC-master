# /utils/influxdb_reader.py

from influxdb_client import InfluxDBClient
from app.config import settings
import logging

class InfluxDBReader:
    def __init__(self):
        # Initialize the InfluxDB client
        self.client = InfluxDBClient(
            url=settings.influxdb_url,
            token=settings.influxdb_token,
            org=settings.influxdb_org
        )
        self.bucket = settings.influxdb_bucket
        self.logger = logging.getLogger(__name__)

    def query_agent_data(self, agent_id: str, start_time: str, end_time: str):
        """
        Query InfluxDB for data from a specific agent between the start_time and end_time.

        Args:
        - agent_id: The ID of the agent whose data is being requested.
        - start_time: The start of the time range (ISO format).
        - end_time: The end of the time range (ISO format).

        Returns:
        - agent_data: The queried data from InfluxDB.
        """
        # Dynamically construct the measurement name
        measurement = f"agent/{agent_id}/data"

        query = (
            f'from(bucket: "{self.bucket}") '
            f'|> range(start: {start_time}, stop: {end_time}) '
            f'|> filter(fn: (r) => r["_measurement"] == "{measurement}")'
        )

        try:
            query_api = self.client.query_api()
            result = query_api.query(org=settings.influxdb_org, query=query)

            # Process the result into a more readable format
            agent_data = []
            for table in result:
                for record in table.records:
                    agent_data.append({
                        "time": record.get_time(),
                        "field": record.get_field(),
                        "value": record.get_value()
                    })
            return agent_data

        except Exception as e:
            self.logger.error(f"Error querying InfluxDB for agent {agent_id}: {e}")
            raise

    def close(self):
        """
        Close the InfluxDB client connection.
        """
        self.client.close()
