import json
import random
import time
import uuid
from pathlib import Path

from kafka import KafkaProducer

TOPIC = "twitter"
BROKER = "localhost:9092"

DATA_FILE = Path(__file__).resolve().parent.parent / "tweets_1000_labeled.jsonl"


def load_comments() -> list[str]:
    comments: list[str] = []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        for line in f:
           try:
               record = json.loads(line)
           except json.JSONDecodeError:
                continue
            text = (
                record.get("comment")
                or record.get("text")
                or record.get("tweet")
                or record.get("content")
            )
            if text:
                comments.append(text)
    return comments


COMMENTS = load_comments()


def generate_message() -> dict:
    return {
        "user_id": f"user_{uuid.uuid4().hex[:8]}",
        "comment": random.choice(COMMENTS),
    }


def run():
    producer = KafkaProducer(
        bootstrap_servers=BROKER,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )
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
 
EOF
)
