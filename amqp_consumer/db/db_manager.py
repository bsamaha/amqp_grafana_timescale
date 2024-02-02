# db_manager.py
import psycopg2
from contextlib import contextmanager
from config import Config
from logger import setup_logger

logger = setup_logger("db_manager")

class DBManager:
    @staticmethod
    def get_connection_params():
        """Provides parameters for database connection."""
        return {
            "host": Config.POSTGRES_HOST,
            "database": Config.POSTGRES_DB,
            "user": Config.POSTGRES_USER,
            "password": Config.POSTGRES_PASSWORD,
        }

    @staticmethod
    @contextmanager
    def get_db_connection():
        """Context manager for database connection."""
        connection = None
        try:
            connection = psycopg2.connect(**DBManager.get_connection_params())
            logger.debug("Successfully connected to the database")
            yield connection
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
        finally:
            if connection:
                connection.close()

    @staticmethod
    @contextmanager
    def get_db_cursor(commit=False):
        """Context manager for database cursor."""
        with DBManager.get_db_connection() as connection:
            cursor = connection.cursor()
            try:
                yield cursor
                if commit:
                    connection.commit()
            except Exception as e:
                connection.rollback()
                raise
            finally:
                cursor.close()

    @staticmethod
    def insert_into_db(data):
        """Generic method to insert JSON data into the specified table."""
        table_name = data.get("message_type").lower()  # Assuming this is safe and validated upstream
        data.pop("message_type", None)  # Remove message_type from data
        
        logger.debug(f"Inserting data into {table_name}")
        logger.debug(f"Data to be inserted: {data}")
        
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
