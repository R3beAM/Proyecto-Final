import json
import random
import time
import uuid

from kafka import KafkaProducer

TOPIC = "twitter"
BROKER = "localhost:9092"

COMMENTS = [
    "I love this!",
    "This is terrible",
    "Amazing work",
    "I hate this!",
    "Could be better",
    "Absolutely fantastic",
]


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
