import psycopg2
from psycopg2 import pool

class PostgresConnector:
    def __init__(self, host, port, dbname, user, password, minconn=5, maxconn=100):
        self.host = host
        self.port = port
        self.dbname = dbname
        self.user = user
        self.password = password
        self.minconn = minconn
        self.maxconn = maxconn
        self.pool = None

    def connect(self):
        """Initialize a thread-safe PostgreSQL connection pool."""
        self.pool = psycopg2.pool.SimpleConnectionPool(
            self.minconn,
            self.maxconn,
            host=self.host,
            port=self.port,
            dbname=self.dbname,
            user=self.user,
            password=self.password
        )
        if not self.pool:
            raise Exception("Failed to initialize PostgreSQL connection pool")

    def get_conn(self):
        """Borrow a connection from the pool."""
        return self.pool.getconn()

    def put_conn(self, conn):
        """Return the connection back to the pool."""
        self.pool.putconn(conn)

    def close_all(self):
        """Close all connections in the pool."""
        if self.pool:
            self.pool.closeall()

    def insert(self, table, record):
        """Insert a single record into the table."""
        conn = self.get_conn()
        try:
            with conn.cursor() as cur:
                columns = ', '.join(record.keys())
                placeholders = ', '.join(['%s'] * len(record))
                query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
                cur.execute(query, tuple(record.values()))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"[ERROR] Failed to insert record id={record.get('id')}, Error: {e}")
            raise
        finally:
            self.put_conn(conn)

    def read_user_by_id(self, table, user_id):
        """Read one record by UUID (thread-safe)."""
        conn = self.get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(f"SELECT * FROM {table} WHERE id = %s", (user_id,))
                result = cur.fetchone()
            return result
        except Exception as e:
            print(f"[ERROR] Failed to read id: {user_id}, Error: {e}")
            raise
        finally:
            self.put_conn(conn)

    def truncate_table(self, table):
        """Clear the table before new insert test."""
        conn = self.get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(f"TRUNCATE TABLE {table} RESTART IDENTITY")
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"[ERROR] Failed to truncate table {table}, Error: {e}")
            raise
        finally:
            self.put_conn(conn)
