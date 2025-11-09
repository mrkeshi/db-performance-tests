


from base_test import BaseLoadTest
from databases.cassandra import KEYSPACE, CASSANDRA_PORT, CASSANDRA_HOST, CassandraConnector


class CassandraLoadTest(BaseLoadTest):
    uuid_as_str = False


if __name__ == "__main__":
    db = CassandraConnector(CASSANDRA_HOST, CASSANDRA_PORT, KEYSPACE)
    db.connect()

    test = CassandraLoadTest(db, num_records=500_000)

    test.run_repeats_insert_concurrent(repeats=5, num_threads=50)
    
    test.run_read_repeats_concurrent(repeats=5, num_threads=50)
    
    test.run_mixed_repeats_concurrent(read_ratio=0.9, repeats=5, num_threads=50)

    test.run_mixed_repeats_concurrent(read_ratio=0.5, repeats=5, num_threads=50)

    test.run_mixed_repeats_concurrent(read_ratio=0.1, repeats=5, num_threads=50)

    test.run_mixed_repeats_concurrent(read_ratio=0.0, repeats=5, num_threads=50)

    db.close()
