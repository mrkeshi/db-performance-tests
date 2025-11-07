import redis

class RedisConnector:
    def __init__(self, host, port, db):
        self.host = host
        self.port = port
        self.db_num = db
        self.client = None

    def connect(self):
        self.client = redis.Redis(host=self.host, port=self.port, db=self.db_num)

    def insert(self, key, data):
        self.client.hset(key, mapping={k: str(v) for k, v in data.items()})

    def truncate_table(self, table_name=None):
        # Redis DB flush
        self.client.flushdb()

    def close(self):
        self.client.close()

    def read_user_by_id(self, key):
        return self.client.hgetall(key)

    def update_user_fields(self, table, key, fields):
        self.client.hset(key, mapping={k: v for k, v in fields.items()})
