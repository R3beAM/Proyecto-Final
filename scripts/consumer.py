import json
import time
from typing import Any

from kafka import KafkaConsumer
from pymongo import MongoClient

TOPIC = "twitter"
BROKER = "localhost:9092"
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "twitter_db"
COLLECTION = "raw_comments"


def run() -> None:
    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=BROKER,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="twitter-group",
    )

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
