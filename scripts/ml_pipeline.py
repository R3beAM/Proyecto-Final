import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from pymongo import MongoClient
import mysql.connector

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "twitter_db"
COLLECTION = "raw_comments"

MYSQL_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "example",
    "database": "twitter",
}

MODEL_NAME = "distilbert-base-uncased-finetuned-sst-2-english"


class SentimentModel:
    def __init__(self) -> None:
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        self.model = (
            AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
            .to(self.device)
            .eval()
        )

    def predict(self, text: str) -> tuple[str, float]:
        inputs = self.tokenizer(text, return_tensors="pt").to(self.device)
        with torch.no_grad():
            logits = self.model(**inputs).logits
            probs = torch.nn.functional.softmax(logits, dim=1)
            score, idx = torch.max(probs, dim=1)
            label = self.model.config.id2label[idx.item()]
            return label, float(score.item())


def run() -> None:
    mongo = MongoClient(MONGO_URI)
    collection = mongo[DB_NAME][COLLECTION]

    mysql_conn = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = mysql_conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tweets (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id VARCHAR(255),
            comment TEXT,
            sentiment VARCHAR(32),
            score FLOAT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    mysql_conn.commit()

    model = SentimentModel()

    while True:
        doc = collection.find_one({"processed": False})
        if not doc:
            print("No more documents to process")
            break

        sentiment, score = model.predict(doc["comment"])
        collection.update_one(
            {"_id": doc["_id"]},
            {"$set": {"processed": True, "sentiment": sentiment, "score": score}},
        )

        cursor.execute(
            "INSERT INTO tweets (user_id, comment, sentiment, score) VALUES (%s, %s, %s, %s)",
            (doc["user_id"], doc["comment"], sentiment, score),
        )
        mysql_conn.commit()
        print(f"Processed {doc['_id']} -> {sentiment} ({score:.4f})")

    cursor.close()
    mysql_conn.close()


if __name__ == "__main__":
    run()
