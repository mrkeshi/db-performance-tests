import string
import uuid
import random
from benchmarks.base_test import BaseLoadTest
from databases.mongo import MongoConnector, MONGO_HOST, MONGO_PORT, DATABASE, USERNAME, PASSWORD

class MongoLoadTest(BaseLoadTest):
    def generate_record(self, i):
        random_fields = [
            "".join(random.choices(string.ascii_letters + string.digits, k=200))
            for _ in range(5)
        ]

        return {
            "_id": str(uuid.UUID(int=i)),
            "client": f"client{i:06d}{random.randint(100000000000, 999999999999)}",
            "name": f"user{i}",
            "email": f"user{i}@example.com",
            "phone": f"+1{random.randint(1000000000, 9999999999)}",
            "age": 20 + i % 50,
            "country": random.choice(["US", "UK", "DE", "FR", "IN"]),
            "attr0": random_fields[0],
            "attr1": random_fields[1],
            "attr2": random_fields[2],
            "attr3": random_fields[3],
            "attr4": random_fields[4],
        }

if __name__ == "__main__":
    db = MongoConnector(MONGO_HOST, MONGO_PORT, DATABASE, USERNAME, PASSWORD)
    db.connect()

    test = MongoLoadTest(db, num_records=500_000)

    test.run_mixed_repeats_concurrent(read_ratio=0.1, repeats=5, num_threads=50)

    db.close()
