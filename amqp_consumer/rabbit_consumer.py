import pika
import time
from config import Config
from logger import setup_logger

# Setup logger for this module
logger = setup_logger("rabbit_consumer")


class RabbitConsumer:
    def __init__(self, queue_name, on_message_callback):
        self.queue_name = queue_name
        self.on_message_callback = on_message_callback
        self.credentials = pika.PlainCredentials(
            Config.RABBITMQ_USER, Config.RABBITMQ_PASS
        )
        self.connection = None
        self.channel = None

    def connect(self):
        """Establishes a connection to RabbitMQ."""
        max_retries = 5
        retry_delay = 5  # seconds
        logger.info("Attempting to connect to RabbitMQ")

        for attempt in range(max_retries):
            try:
                self.connection = pika.BlockingConnection(
                    pika.ConnectionParameters(
                        host=Config.RABBITMQ_HOST, credentials=self.credentials
                    )
                )
                self.channel = self.connection.channel()
                self.channel.queue_declare(queue=self.queue_name, durable=True)
                self.channel.basic_consume(
                    queue=self.queue_name,
                    on_message_callback=self.on_message_callback,
                    auto_ack=True,
                )
                logger.info("Successfully connected to RabbitMQ and declared queue")
                break  # Connection successful
            except pika.exceptions.AMQPConnectionError as e:
                logger.warning(
                    f"Connection attempt {attempt + 1} of {max_retries} failed. Retrying in {retry_delay} seconds..."
                )
                time.sleep(retry_delay)
                if attempt == max_retries - 1:
                    logger.error(
                        "Max retries reached. Could not establish connection to RabbitMQ."
                    )
                    raise e

    def start_consuming(self):
        """Starts consuming messages from RabbitMQ."""
        if self.connection and self.channel:
            logger.info("RabbitMQ consumer started. Waiting for messages...")
            self.channel.start_consuming()
