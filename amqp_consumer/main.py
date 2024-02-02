# main.py
from db.db_manager import DBManager
from rabbit_consumer import RabbitConsumer
from config import Config
import json


def on_message_received(ch, method, properties, body):
    json_data = json.loads(body)
    print(f"Received data: {json_data}")
    # Insert into PostgreSQL using DBManager
    DBManager.insert_into_db(json_data)


def main():
    rabbit_consumer = RabbitConsumer(Config.RABBITMQ_QUEUE, on_message_received)
    rabbit_consumer.connect()
    rabbit_consumer.start_consuming()


if __name__ == "__main__":
    main()
