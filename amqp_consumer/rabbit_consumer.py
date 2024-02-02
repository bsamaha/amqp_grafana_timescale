import pika
import time
from config import Config
from logger import setup_logger

logger = setup_logger("rabbit_consumer")

class RabbitMQConnection:
    """Handles the connection to RabbitMQ."""

    def __init__(self, host, credentials, retry_attempts=5, retry_delay=10):
        self.host = host
        self.credentials = credentials
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay

    def connect(self):
        """Attempt to connect to RabbitMQ with retries."""
        for attempt in range(self.retry_attempts):
            try:
                connection = pika.BlockingConnection(
                    pika.ConnectionParameters(
                        host=self.host,
                        credentials=self.credentials,
                        heartbeat=600,
                        blocked_connection_timeout=300 
                    )
                )
                logger.info("Successfully connected to RabbitMQ")
                return connection
            except pika.exceptions.AMQPConnectionError as e:
                if attempt < self.retry_attempts - 1:
                    logger.warning(f"Connection attempt {attempt + 1} failed, retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    logger.error("Failed to connect to RabbitMQ after all attempts")
                    raise

class RabbitConsumer:
    """Consumes messages from a RabbitMQ queue."""

    def __init__(self, queue_name, on_message_callback):
        self.queue_name = queue_name
        self.on_message_callback = on_message_callback
        self.connection = None
        self.channel = None

    def setup_connection(self):
        """Sets up RabbitMQ connection and channel with retry logic."""
        connection_handler = RabbitMQConnection(
            Config.RABBITMQ_HOST,
            pika.PlainCredentials(Config.RABBITMQ_USER, Config.RABBITMQ_PASS)
        )
        self.connection = connection_handler.connect()
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name, durable=True)
        self.channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=self.on_message_callback,
            auto_ack=True,
        )

    def start_consuming(self):
        """Starts consuming messages from RabbitMQ."""
        try:
            self.setup_connection()
            logger.info("RabbitMQ consumer started. Waiting for messages...")
            self.channel.start_consuming()
        except Exception as e:
            logger.error(f"Error starting consumer: {e}")
            self.close_connection()

    def close_connection(self):
        """Gracefully closes the channel and connection."""
        if self.channel:
            self.channel.close()
        if self.connection:
            self.connection.close()
        logger.info("RabbitMQ connection and channel closed.")

