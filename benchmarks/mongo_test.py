import string
import uuid
import random
from benchmarks.base_test import BaseLoadTest
from databases.mongo import MongoConnector, MONGO_HOST, MONGO_PORT, DATABASE, USERNAME, PASSWORD

class MongoLoadTest(BaseLoadTest):
    uuid_as_str = True

if __name__ == "__main__":
    db = MongoConnector(MONGO_HOST, MONGO_PORT, DATABASE, USERNAME, PASSWORD)
    db.connect()
    
    test = MongoLoadTest(db, num_records=500_000)

    test.run_repeats_insert_concurrent(repeats=5, num_threads=50)
    
    test.run_read_repeats_concurrent(repeats=5, num_threads=50)
    
    test.run_mixed_repeats_concurrent(read_ratio=0.9, repeats=5, num_threads=50)

    test.run_mixed_repeats_concurrent(read_ratio=0.5, repeats=5, num_threads=50)

    test.run_mixed_repeats_concurrent(read_ratio=0.1, repeats=5, num_threads=50)

    test.run_mixed_repeats_concurrent(read_ratio=0.0, repeats=5, num_threads=50)

    db.close()
