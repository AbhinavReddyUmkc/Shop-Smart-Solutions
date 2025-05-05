# services/database.py
import os
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Connection parameters from env (with sensible defaults)
DB_NAME = os.environ.get("DB_NAME", "threat_intelligence")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASS = os.environ.get("DB_PASS", "1234")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")

logger.info(f"DB params: {DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

@contextmanager
def get_db_connection():
    """
    Yields a psycopg2 connection (with RealDictCursor as default cursor_factory).
    """
    conn = None
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST,
            port=DB_PORT
        )
        yield conn
    except Exception as e:
        logger.error(f"Error connecting to Postgres: {e}")
        raise
    finally:
        if conn:
            conn.close()
            logger.info("Closed DB connection")

@contextmanager
def get_db_cursor():
    """
    Yields a cursor that returns rows as dicts.
    Commits on success, rolls back on exception.
    """
    with get_db_connection() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
            yield cur
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()
