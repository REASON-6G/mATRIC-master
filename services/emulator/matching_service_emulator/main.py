import asyncio
import logging
import os
import random
from datetime import datetime
from logging.handlers import RotatingFileHandler
from bson import ObjectId
from faker import Faker
from quart import Quart
from jsonschema import Draft4Validator, ValidationError
from matching_service_client.matching_service_client import MatchingServiceClient
from pymongo import MongoClient

# -------------------------
# Config
# -------------------------
class Config:
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://admin:changeme@localhost:27017/matchingservice")
    API_URL = os.getenv("API_URL", "http://localhost:5000")
    LOG_DIR = os.getenv("LOG_DIR", "logs")
    POLL_INTERVAL = 2  # seconds

os.makedirs(Config.LOG_DIR, exist_ok=True)

# -------------------------
# App & DB
# -------------------------
app = Quart(__name__)
mongo_client = MongoClient(Config.MONGO_URI)
db = mongo_client.get_default_database()
fake = Faker()

# -------------------------
# Globals
# -------------------------
running_emulator_tasks = {}

# -------------------------
# JSON Schema Message Generator
# -------------------------
def generate_message(schema: dict) -> dict:
    """
    Generate a random message based on a JSON Schema (Draft-04).
    Supports primitive types, nested objects, and arrays.
    """
    validator = Draft4Validator(schema)

    def generate_for_schema(sch):
        sch_type = sch.get("type")
        if sch_type == "object":
            msg = {}
            props = sch.get("properties", {})
            for prop, prop_schema in props.items():
                msg[prop] = generate_for_schema(prop_schema)
            # Ensure required fields exist
            for req in sch.get("required", []):
                if req not in msg:
                    msg[req] = None
            return msg

        elif sch_type == "array":
            items_schema = sch.get("items", {})
            length = random.randint(1, 3)
            
            # Handle tuple validation (list of schemas)
            if isinstance(items_schema, list):
                return [generate_for_schema(items_schema[i % len(items_schema)]) for i in range(length)]
            else:
                return [generate_for_schema(items_schema) for _ in range(length)]


        elif sch_type == "integer":
            return random.randint(0, 100)
        elif sch_type == "number":
            return round(random.uniform(0, 100), 2)
        elif sch_type == "string":
            return fake.word()
        elif sch_type == "boolean":
            return random.choice([True, False])
        else:
            return None

    message = generate_for_schema(schema)

    # Validate message against schema
    errors = list(validator.iter_errors(message))
    if errors:
        logging.warning(f"Generated message validation errors: {errors}")

    return message


# -------------------------
# Emulator Task
# -------------------------
async def run_emulator_task(emulator_doc):
    emulator_id = str(emulator_doc["_id"])
    publisher_id = emulator_doc.get("publisher_id")

    # Fetch publisher API token
    publisher_doc = db.publishers.find_one({"_id": ObjectId(publisher_id)})
    if not publisher_doc:
        return
    api_token = publisher_doc.get("api_token")
    if not api_token:
        return

    # Logging setup
    logger = logging.getLogger(f"emulator_{emulator_id}")
    logger.setLevel(logging.INFO)
    if logger.hasHandlers():
        logger.handlers.clear()
    fh = RotatingFileHandler(
        os.path.join(Config.LOG_DIR, f"emulator_{emulator_id}.log"),
        maxBytes=2 * 1024 * 1024,
        backupCount=3
    )
    fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(fh)

    # Client auth using token
    client = MatchingServiceClient(Config.API_URL)
    await client.login_with_token(api_token)
    logger.info(f"Emulator {emulator_id} started")

    try:
        while True:
            # Refresh emulator config
            emulator_doc = db.emulators.find_one({"_id": ObjectId(emulator_id)})
            if not emulator_doc or not emulator_doc.get("running"):
                break

            interval = emulator_doc.get("interval", 1)
            topic_id = emulator_doc.get("topic_id")
            schema = emulator_doc.get("msg_schema")

            # Skip iteration if topic or schema missing
            if not topic_id:
                logger.warning(f"No topic_id set for emulator {emulator_id}, skipping iteration")
                await asyncio.sleep(interval)
                continue

            topic_doc = db.topics.find_one({"_id": ObjectId(topic_id)})
            if not topic_doc or not topic_doc.get("topic"):
                logger.warning(f"Topic {topic_id} not found, skipping iteration")
                await asyncio.sleep(interval)
                continue

            topic = topic_doc["topic"]

            if not schema:
                logger.warning(f"No schema set for emulator {emulator_id}, skipping iteration")
                await asyncio.sleep(interval)
                continue

            # Generate message using JSON Schema
            try:
                message = generate_message(schema)
                if not message:
                    raise ValueError("Generated message is empty")
            except Exception as e:
                logger.error(f"Failed to generate message: {e}")
                await asyncio.sleep(interval)
                continue

            # Publish
            try:
                await client.publish(topic, message)
                logger.info(f"Published to {topic}: {message}")
            except Exception as e:
                logger.error(f"Publish error: {e}")

            await asyncio.sleep(interval)

    finally:
        await client.close()
        logger.info(f"Emulator {emulator_id} stopped")
        for handler in logger.handlers:
            handler.close()
            logger.removeHandler(handler)
        running_emulator_tasks.pop(emulator_id, None)

# -------------------------
# Polling Loop
# -------------------------
async def emulator_polling_loop():
    while True:
        emulator_docs = list(db.emulators.find({}))
        for doc in emulator_docs:
            eid = str(doc["_id"])
            running_flag = doc.get("running", False)
            topic_id = doc.get("topic_id")
            schema = doc.get("msg_schema")

            # Determine if emulator is valid to run
            is_valid = running_flag and topic_id and schema
            if is_valid and eid not in running_emulator_tasks:
                logging.info("Starting emulator task %s", eid)
                task = asyncio.create_task(run_emulator_task(doc))
                running_emulator_tasks[eid] = task

            elif (not is_valid or not running_flag) and eid in running_emulator_tasks:
                logging.info("Stopping emulator task %s", eid)
                task = running_emulator_tasks.pop(eid, None)
                if task:
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        logging.info("Emulator task %s cancelled", eid)

        await asyncio.sleep(Config.POLL_INTERVAL)

# -------------------------
# Startup
# -------------------------
@app.before_serving
async def startup():
    asyncio.create_task(emulator_polling_loop())

# -------------------------
# Run App
# -------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=6000)
