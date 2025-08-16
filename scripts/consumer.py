import json
import os
import time
from typing import Any

from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
from pymongo import MongoClient

TOPIC = "twitter"
BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "twitter_db"
COLLECTION = "raw_comments"


def _create_consumer(max_retries: int = 5, delay: int = 5) -> KafkaConsumer:
    """Create a KafkaConsumer waiting for the broker to be available."""

    for attempt in range(1, max_retries + 1):
        try:
            return KafkaConsumer(
                TOPIC,
                bootstrap_servers=BROKER,
                value_deserializer=lambda v: json.loads(v.decode("utf-8")),
                auto_offset_reset="earliest",
                enable_auto_commit=True,
                group_id="twitter-group",
            )
        except NoBrokersAvailable:
            if attempt == max_retries:
                raise
            print(
                f"Kafka broker at '{BROKER}' not available, retrying in {delay} seconds..."
            )
            time.sleep(delay)


def run() -> None:
    consumer = _create_consumer()

    mongo = MongoClient(MONGO_URI)
    collection = mongo[DB_NAME][COLLECTION]

    for message in consumer:
        data: Any = message.value
        record = {
            "user_id": data["user_id"],
            "comment": data["comment"],
            "timestamp": time.time(),
            "processed": False,
        }
        collection.insert_one(record)
        print(f"Stored: {record}")


if __name__ == "__main__":
    run()
