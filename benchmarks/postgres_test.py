import random
import string
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from benchmarks.base_test import BaseLoadTest
from databases.postgres import PostgresConnector


class PostgresLoadTest(BaseLoadTest):
    uuid_as_str = True

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
