import psycopg2
from config import Config


class DBManager:
    @staticmethod
    def get_postgres_connection():
        """Establishes a connection to the PostgreSQL database."""
        return psycopg2.connect(
            host=Config.POSTGRES_HOST,
            database=Config.POSTGRES_DB,
            user=Config.POSTGRES_USER,
            password=Config.POSTGRES_PASSWORD,
        )

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
                print("Dropped message: 'device_id' not found in the message")
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
        except Exception as e:
            print(f"Database error: {e}")
            conn.rollback()
        finally:
            cur.close()
            conn.close()
