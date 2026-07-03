from mysql.connector import pooling
from config import DB_CONFIG, POOL_SIZE

connection_pool = pooling.MySQLConnectionPool(
    pool_name="lookup_pool",
    pool_size=POOL_SIZE,
    **DB_CONFIG,
)

def get_db():
    """Get a connection from the pool (auto-returned when closed)."""
    return connection_pool.get_connection()