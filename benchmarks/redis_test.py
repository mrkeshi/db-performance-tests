import uuid
import random
import string
import time
import psutil
from benchmarks.base_test import BaseLoadTest
from databases.redis import RedisConnector, REDIS_HOST, REDIS_PORT, REDIS_DB

class RedisLoadTest(BaseLoadTest):
    def generate_record(self, i):
        random_fields = [
            "".join(random.choices(string.ascii_letters + string.digits, k=200))
            for _ in range(5)
        ]
        return {
            "_id": str(uuid.UUID(int=i)),
            "client": f"client{i:06d}{random.randint(100000000000,999999999999)}",
            "name": f"user{i}",
            "email": f"user{i}@example.com",
            "phone": f"+1{random.randint(1000000000,9999999999)}",
            "age": 20 + i % 50,
            "country": random.choice(["US", "UK", "DE", "FR", "IN"]),
            "attr0": random_fields[0],
            "attr1": random_fields[1],
            "attr2": random_fields[2],
            "attr3": random_fields[3],
            "attr4": random_fields[4],
        }

    def _insert_chunk(self, start, end):
        latencies = []
        for i in range(start, end):
            record = self.generate_record(i)
            key = str(record["_id"])
            start_t = time.time()
            self.db.insert(key, record)
            end_t = time.time()
            latencies.append(end_t - start_t)
        return latencies

    def _read_chunk(self, start, end):
        latencies = []
        for i in range(start, end):
            key = str(uuid.UUID(int=i))
            start_t = time.time()
            record = self.db.read_user_by_id(key)
            end_t = time.time()
            latencies.append(end_t - start_t)
        return latencies

    def mixed_chunk(self, start, end, read_ratio=0.1):
        local_latencies = []

        def random_string(n=100):
            import string
            return ''.join(random.choices(string.ascii_letters + string.digits, k=n))

        for i in range(start, end):
            start_t = time.time()
            key = str(uuid.UUID(int=i))

            if random.random() < read_ratio:
                self.db.read_user_by_id(key)
            else:
                updates = {
                    "attr0": random_string(100),
                    "attr1": random_string(100),
                    "attr2": random_string(100)
                }
                self.db.update_user_fields("users", key, updates)

            end_t = time.time()
            local_latencies.append(end_t - start_t)

        return local_latencies


if __name__ == "__main__":
    db = RedisConnector(REDIS_HOST, REDIS_PORT, REDIS_DB)
    db.connect()

    test = RedisLoadTest(db, num_records=500_000)
    test.run_mixed_repeats_concurrent(read_ratio=0.1, repeats=5, num_threads=50)
    db.close()
