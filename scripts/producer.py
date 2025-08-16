import json
import os
import random
import time
import uuid
from pathlib import Path

from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

TOPIC = "twitter"
# Allow broker configuration via environment variable for flexibility in
# different deployment environments.  Default to the local Kafka instance
# used during development.
BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")

DATA_FILE = Path(__file__).resolve().parent.parent / "tweets_1000_labeled.jsonl"


def load_messages() -> list[dict[str, str]]:
    messages: list[dict[str, str]] = []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            comment = (
                record.get("comment")
                or record.get("text")
                or record.get("tweet")
                or record.get("content")
            )
            if comment:
                user = record.get("user_id") or f"user_{uuid.uuid4().hex[:8]}"
                messages.append({"user_id": user, "comment": comment})
    return messages


MESSAGES = load_messages()


def generate_message() -> dict[str, str]:
    return random.choice(MESSAGES)


def create_producer(retries: int = 5, delay: float = 1.0) -> KafkaProducer | None:
    """Create a Kafka producer with simple retry logic.

    If the Kafka broker is not available, the function will retry a few times
    before giving up and returning ``None``.  This prevents the script from
    crashing with a ``NoBrokersAvailable`` error when Kafka is temporarily
    unreachable.
    """

    for attempt in range(retries):
        try:
            return KafkaProducer(
                bootstrap_servers=BROKER,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            )
        except NoBrokersAvailable:
            if attempt == retries - 1:
                break
            time.sleep(delay)
    return None


def run() -> None:
    producer = create_producer()
    if producer is None:
        print("Kafka broker is not available. Exiting.")
        return

    num_messages = random.randint(5, 15)
    for _ in range(num_messages):
        msg = generate_message()
        producer.send(TOPIC, msg)
        producer.flush()
        print(f"Sent: {msg}")
        time.sleep(random.uniform(0.5, 3.0))

    producer.close()


if __name__ == "__main__":
    run()
