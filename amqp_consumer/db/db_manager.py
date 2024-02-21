import time
import psycopg2
from psycopg2 import pool
from contextlib import contextmanager
from config import Config
from logger import setup_logger
import os

logger = setup_logger(__name__, level=os.environ.get("LOG_LEVEL", "INFO"))

class DBManager:
    _connection_pool = None

    @classmethod
    def initialize_connection_pool(cls, max_retries=10, initial_delay=3):
        """
        Initialize the database connection pool with retry logic, doubling the delay after each attempt.

        Parameters:
        - max_retries: Maximum number of connection attempts.
        - initial_delay: Initial delay in seconds between connection attempts, doubles after each retry.
        """
        delay_between_retries = initial_delay
        for attempt in range(1, max_retries + 1):
            try:
                cls._connection_pool = pool.SimpleConnectionPool(
                    1, 10,  # min and max connections
                    host=Config.POSTGRES_HOST,
                    database=Config.POSTGRES_DB,
                    user=Config.POSTGRES_USER,
                    password=Config.POSTGRES_PASSWORD,
                )
                logger.info("Database connection pool initialized successfully.")
                break  # Exit loop if connection is successful
            except psycopg2.OperationalError as e:
                logger.error("Attempt %s failed: %s", attempt, e)
                if attempt == max_retries:
                    logger.error("All attempts to connect to the database have failed.")
                    raise
                else:
                    time.sleep(delay_between_retries)
                    delay_between_retries += initial_delay  # Double the delay for the next retry

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
            logger.error("Database operation failed: %s", e)
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
                logger.debug("Executing query: %s with values %s", query, values)  # Log the query and values
                logger.debug("Data inserted successfully into %s", table_name)
            except Exception as e:
                logger.error("Error inserting data into %s: %s", table_name, e)
                logger.error("Failed query: %s with values %s", query, values)  # Log the failed query and values
                raise

# Additional CRUD Operations for DBManager

    @staticmethod
    def get_item_by_id(table_name, record_id):
        """Fetch a record by its ID from the specified table.
        
        Parameters:
        - table_name: Name of the table to fetch from.
        - record_id: ID of the record to fetch.
        """
        with DBManager.get_db_cursor() as cur:
            query = f"SELECT * FROM {table_name} WHERE id = %s"
            cur.execute(query, (record_id,))
            result = cur.fetchone()
            if result:
                logger.debug("Record fetched successfully from %s", table_name)
                return result
            else:
                logger.debug("No record found in %s with ID %s", table_name, record_id)
                return None

    @staticmethod
    def update_experiment_description(experiment_id: int, new_description: str):
        """Update the description for a specific experiment."""
        with DBManager.get_db_cursor(commit=True) as cur:
            query = "UPDATE experiments SET description = %s WHERE id = %s"
            cur.execute(query, (new_description, experiment_id))
            logger.debug("Experiment description updated successfully.")

    @staticmethod
    def delete_device(device_id):
        """Delete a device record by its ID."""
        with DBManager.get_db_cursor(commit=True) as cur:
            query = "DELETE FROM hardware WHERE id = %s"
            cur.execute(query, (device_id,))
            logger.debug("Device deleted successfully.")
