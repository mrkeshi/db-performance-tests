from cassandra.cluster import Cluster


class CassandraConnector:
    def __init__(self, host, port, keyspace):
        self.host = host
        self.port = port
        self.keyspace = keyspace
        self.cluster = None
        self.session = None

    def connect(self):
        self.cluster = Cluster([self.host], port=self.port)
        self.session = self.cluster.connect(self.keyspace)

    def insert(self, table, data):
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        self.session.execute(query, tuple(data.values()))

    def truncate_table(self, table):
        self.session.execute(f"TRUNCATE TABLE {table}")

    def close(self):
        self.cluster.shutdown()

    def read_user_by_id(self, table, id):
        query = f"SELECT * FROM {table} WHERE id = %s"
        return self.session.execute(query, (id,))

    def read_user_by_name(self, table, name):
        query = f"SELECT * FROM {table} WHERE name = %s ALLOW FILTERING"
        return self.session.execute(query, (name,))

    def update_user_fields(self, table, id, fields):
        set_clause = ', '.join([f"{col} = %s" for col in fields.keys()])
        values = list(fields.values()) + [id]
        query = f"UPDATE {table} SET {set_clause} WHERE id = %s"
        self.session.execute(query, values)