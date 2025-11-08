import uuid
import random
import string
import time
import psutil
from benchmarks.base_test import BaseLoadTest
from databases.redis import RedisConnector, REDIS_HOST, REDIS_PORT, REDIS_DB

class RedisLoadTest(BaseLoadTest):
    uuid_as_str = True


if __name__ == "__main__":
    db = RedisConnector(REDIS_HOST, REDIS_PORT, REDIS_DB)
    db.connect()

    test = RedisLoadTest(db, num_records=500_000)
    test.run_mixed_repeats_concurrent(read_ratio=0.1, repeats=5, num_threads=50)
    db.close()
