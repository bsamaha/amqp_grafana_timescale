import psycopg2
from config import Config
from logger import setup_logger

# Setup logger for this module
logger = setup_logger("db_manager")


class DBManager:
    @staticmethod
    def get_postgres_connection():
        try:
            connection = psycopg2.connect(
                host=Config.POSTGRES_HOST,
                database=Config.POSTGRES_DB,
                user=Config.POSTGRES_USER,
                password=Config.POSTGRES_PASSWORD,
            )
            logger.debug("Successfully connected to the database")
            return connection
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise e

    @staticmethod
    def insert_into_db(json_data):
        """Inserts JSON data into the database."""
        conn = DBManager.get_postgres_connection()
        cur = conn.cursor()

        # Convert 'processed_time' to an integer
        json_data["processed_time"] = int(float(json_data["processed_time"]))

        try:
            # Check if 'device_id' key exists in the JSON data
            if "device_id" not in json_data:
                logger.warning("Dropped message: 'device_id' not found in the message")
                return

            cur.execute(
                """
                INSERT INTO gngga (
                    full_time, lat, ns, lon, ew, quality,
                    num_sv, hdop, alt, alt_unit, sep, sep_unit,
                    diff_age, diff_station, processed_time, device_id
                ) VALUES (
                    %(full_time)s, %(lat)s, %(ns)s, %(lon)s, %(ew)s, %(quality)s,
                    %(num_sv)s, %(hdop)s, %(alt)s, %(alt_unit)s, %(sep)s, %(sep_unit)s,
                    %(diff_age)s, %(diff_station)s, %(processed_time)s, %(device_id)s
                )
                """,
                json_data,
            )
            conn.commit()
            logger.debug("Data inserted successfully into the database")

        except Exception as e:
            logger.error(f"Database error during insertion: {e}")
            conn.rollback()
        finally:
            cur.close()
            conn.close()
