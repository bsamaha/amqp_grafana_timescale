from db.db_manager import DBManager
from rabbit_consumer import RabbitConsumer
from config import Config
import json
from logger import setup_logger
from message_processors.processor_factory import get_processor

# Setup logger for this module
logger = setup_logger(__name__)


def on_message_received(ch, method, properties, body):
    message_data = json.loads(body)
    logger.info(f"Received data: {message_data}")

    try:
        processor = get_processor(message_data)
        processor.process()
        logger.info(f"Processed {message_data} message successfully.")
    except ValueError as e:
        logger.error(f"Failed to process message: {e}")


def main():
    logger.info("Application started")
    # Initialize RabbitConsumer with the queue name and callback function
    rabbit_consumer = RabbitConsumer(Config.RABBITMQ_QUEUE, on_message_received)
    # Start consuming messages, which includes connecting to RabbitMQ
    rabbit_consumer.start_consuming()


if __name__ == "__main__":
    main()
