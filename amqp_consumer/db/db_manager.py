import time
import psycopg2
from psycopg2 import pool
from contextlib import contextmanager
from config import Config
from logger import setup_logger

logger = setup_logger("db_manager")

class DBManager:
    _connection_pool = None

    @classmethod
    def initialize_connection_pool(cls, max_retries=10, delay_between_retries=5):
        """
        Initialize the database connection pool with retry logic.

        Parameters:
        - max_retries: Maximum number of connection attempts.
        - delay_between_retries: Delay in seconds between connection attempts.
        """
        for attempt in range(1, max_retries + 1):
            try:
                cls._connection_pool = psycopg2.pool.SimpleConnectionPool(
                    1, 10,  # min and max connections
                    host=Config.POSTGRES_HOST,
                    database=Config.POSTGRES_DB,
                    user=Config.POSTGRES_USER,
                    password=Config.POSTGRES_PASSWORD,
                )
                logger.info("Database connection pool initialized successfully.")
                break  # Exit loop if connection is successful
            except psycopg2.OperationalError as e:
                logger.error(f"Attempt {attempt} failed: {e}")
                if attempt == max_retries:
                    logger.error("All attempts to connect to the database have failed.")
                    raise
                else:
                    time.sleep(delay_between_retries)

    @staticmethod
    @contextmanager
    def get_db_cursor(commit=False):
        connection = None
        try:
            connection = DBManager._connection_pool.getconn()
            cursor = connection.cursor()
            yield cursor
            if commit:
                connection.commit()
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"Database operation failed: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                DBManager._connection_pool.putconn(connection)

    @staticmethod
    def insert_into_db(table_name, data):
        """Generic method to insert JSON data into the specified table."""
      
        with DBManager.get_db_cursor(commit=True) as cur:
            placeholders = ", ".join(["%s"] * len(data))
            columns = ", ".join(data.keys())
            values = tuple(data.values())
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            try:
                cur.execute(query, values)
                logger.debug(f"Data inserted successfully into {table_name}")
            except Exception as e:
                logger.error(f"Error inserting data into {table_name}: {e}")
                raise
