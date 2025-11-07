import random
import string
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from benchmarks.base_test import BaseLoadTest
from databases.postgres import PostgresConnector


class PostgresLoadTest(BaseLoadTest):
    def generate_record(self, i):
        random_fields = [
            "".join(random.choices(string.ascii_letters + string.digits, k=200))
            for _ in range(5)
        ]
        return {
             "id": str(uuid.UUID(int=i) ),
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

    def _read_chunk(self, start, end):
        latencies = []
        for i in range(start, end):
            record_id = str(uuid.UUID(int=i))
            start_t = time.time()
            _ = self.db.read_user_by_id("users", record_id)
            end_t = time.time()
            latencies.append(end_t - start_t)
        return latencies


if __name__ == "__main__":
    from databases.postgres import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD

    db = PostgresConnector(
        POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
    )
    db.connect()

    num_records = 500_000
    test = PostgresLoadTest(db, num_records=num_records)

    # print("\n=== Starting INSERT Benchmark ===")
    # test.run_repeats_insert_concurrent(repeats=5, num_threads=50)

    print("\n=== Starting READ Benchmark ===")
    test.run_read_repeats_concurrent(repeats=5, num_threads=50)

    db.close_all()
