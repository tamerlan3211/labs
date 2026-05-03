import psycopg2
from config import load_config


def connect(config=None):
    """Return a live psycopg2 connection.  Loads config automatically if omitted."""
    if config is None:
        config = load_config()
    try:
        conn = psycopg2.connect(**config)
        return conn
    except (psycopg2.DatabaseError, Exception) as error:
        print('Connection error:', error)
        raise


if __name__ == '__main__':
    conn = connect()
    print('Connected to the PostgreSQL server.')
    conn.close()
