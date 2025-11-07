from pymongo import MongoClient

from pymongo import MongoClient

class MongoConnector:
    def __init__(self, host, port, database, username, password):
        self.host = host
        self.port = port
        self.database_name = database
        self.username = username
        self.password = password
        self.client = None
        self.db = None

    def connect(self):
        self.client = MongoClient(
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            authSource="admin"
        )
        self.db = self.client[self.database_name]
        self.collection = self.db["users"]

    def insert(self, table, record):
        if "_id" in record and not isinstance(record["_id"], str):
            record["_id"] = str(record["_id"])
        self.db[table].insert_one(record)

    def truncate_table(self, table):
        self.db[table].delete_many({})

    def close(self):
        self.client.close()

    def read_user_by_id(self, table, id):
        if not isinstance(id, str):
            id = str(id)
        return self.db[table].find_one({"_id": id})

    def read_user_by_name(self, table, name):
        return self.db[table].find_one({"name": name})

    def count_records(self, table):
        try:
            count = self.db[table].count_documents({})
            print(f"[INFO] Table '{table}' has {count} records.")
            return count
        except Exception as e:
            print(f"[ERROR] Failed to count records in '{table}', Error: {e}")
            raise

    def update_user_fields(self, table, id, fields):
        if not isinstance(id, str):
            id = str(id)
        self.db[table].update_one({"_id": id}, {"$set": fields})
