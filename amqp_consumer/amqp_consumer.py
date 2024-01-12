import time
import pika
import psycopg2
import json

# PostgreSQL connection parameters
POSTGRES_HOST = "timescaledb"
POSTGRES_DB = "postgres"
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "password"

# RabbitMQ connection parameters
RABBITMQ_HOST = "rabbitmq"
RABBITMQ_QUEUE = "gnss_data_queue"
RABBITMQ_USER = "guest"
RABBITMQ_PASS = "guest"


# Connect to PostgreSQL database
def get_postgres_connection():
    return psycopg2.connect(
        host=POSTGRES_HOST,
        database=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
    )


def insert_into_db(json_data):
    conn = get_postgres_connection()
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


# Callback function when message is received
def on_message_received(ch, method, properties, body):
    json_data = json.loads(body)
    print(f"Received data: {json_data}")

    # Insert into PostgreSQL
    insert_into_db(json_data)


# Connect to RabbitMQ and start consuming
def main():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    connection = None
    max_retries = 5
    retry_delay = 5  # seconds

    for attempt in range(max_retries):
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials)
            )
            break  # Connection successful
        except pika.exceptions.AMQPConnectionError as e:
            if attempt < max_retries - 1:
                print(
                    f"Connection attempt {attempt + 1} of {max_retries} failed. Retrying in {retry_delay} seconds..."
                )
                time.sleep(retry_delay)
            else:
                print(
                    "Max retries reached. Could not establish connection to RabbitMQ."
                )
                raise e

    if connection is not None:
        channel = connection.channel()
        channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
        channel.basic_consume(
            queue=RABBITMQ_QUEUE, on_message_callback=on_message_received, auto_ack=True
        )

        print(" [*] Waiting for messages. To exit press CTRL+C")
        channel.start_consuming()


if __name__ == "__main__":
    main()
