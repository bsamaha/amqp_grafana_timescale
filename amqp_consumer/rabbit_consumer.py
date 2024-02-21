import pika
import json
from config import Config
from logger import setup_logger
import time

logger = setup_logger("rabbit_consumer", level="INFO")

class RabbitMQConnection:
    """Handles the connection to RabbitMQ."""
    def __init__(self, host, credentials, retry_attempts=5, retry_delay=10):
        logger.debug("Initializing RabbitMQConnection with host: %s, retry_attempts: %d, retry_delay: %d", host, retry_attempts, retry_delay)
        self.host = host
        self.credentials = credentials
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay

    def connect(self):
        """Attempt to connect to RabbitMQ with retries."""
        logger.debug("Attempting to connect to RabbitMQ")
        for attempt in range(self.retry_attempts):
            try:
                logger.debug("Connection attempt %d to host %s", attempt + 1, self.host)
                connection = pika.BlockingConnection(
                    pika.ConnectionParameters(
                        host=self.host,
                        credentials=self.credentials,
                        heartbeat=600,
                        blocked_connection_timeout=300 
                    )
                )
                logger.info("Successfully connected to RabbitMQ on attempt %d", attempt + 1)
                return connection
            except pika.exceptions.AMQPConnectionError as e:
                logger.warning("Attempt %d failed with error: %s", attempt + 1, e)
                if attempt < self.retry_attempts - 1:
                    logger.debug("Retrying in %d seconds...", self.retry_delay)
                    time.sleep(self.retry_delay)
                else:
                    logger.error("Failed to connect to RabbitMQ after %d attempts", self.retry_attempts)
                    raise

class RabbitConsumer:
    """Consumes messages from RabbitMQ queues."""
    def __init__(self, processor_factory):
        logger.debug("Initializing RabbitConsumer")
        self.processor_factory = processor_factory
        self.connection = None
        self.channel = None
        self.queues = {
            "gnss_data_queue": "basic",
            "device_registration": "rpc",
            "experiment_registration": "rpc"
        }

    def setup_connection(self):
        logger.debug("Setting up RabbitMQ connection")
        connection_handler = RabbitMQConnection(
            Config.RABBITMQ_HOST,
            pika.PlainCredentials(Config.RABBITMQ_USER, Config.RABBITMQ_PASS)
        )
        self.connection = connection_handler.connect()
        self.channel = self.connection.channel()
        logger.info("RabbitMQ connection and channel setup complete")

    def close_connection(self):
        if self.channel is not None:
            try:
                self.channel.close()
            except Exception as e:
                logger.error("Failed to close channel: %s", e)
        if self.connection is not None:
            try:
                self.connection.close()
            except Exception as e:
                logger.error("Failed to close connection: %s", e)
        logger.info("Connection and channel closed")

    def on_message_callback(self, ch, method, properties, body):
        logger.debug("Received message: %s", body)
        try:
            message_data = json.loads(body)
            logger.debug("Message data parsed: %s", message_data)
        except Exception as e:
            logger.error("Failed to parse message: %s", e)
            ch.basic_nack(delivery_tag=method.delivery_tag)
            return
        try:
            logger.debug("Processing message: %s", message_data)
            logger.debug("Properties: %s", properties)
            processor = self.processor_factory(message_data)
            response = processor.process()
            if properties.reply_to:
                # Use the dedicated publish_message method
                self.publish_message(
                    exchange='',
                    routing_key=properties.reply_to,
                    properties=pika.BasicProperties(correlation_id=properties.correlation_id),
                    body=json.dumps(response)
                )
                logger.info("Processed message successfully response (response, recipeint): %s, %s", response, properties.reply_to)
                logger.debug("Published response to RPC queue: %s", properties.reply_to)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logger.error("Failed to process message: %s", e)
            ch.basic_nack(delivery_tag=method.delivery_tag)

    def start_consuming(self):
        logger.debug("Starting message consumption")
        while True:
            try:
                self.setup_connection()
                logger.info("RabbitMQ consumer started. Waiting for messages...")
                for queue_name in self.queues:
                    self.channel.basic_consume(
                        queue=queue_name,
                        on_message_callback=self.on_message_callback,
                        auto_ack=False,
                    )
                    logger.debug("Queue %s is set for consuming", queue_name)
                self.channel.start_consuming()
            except Exception as e:
                logger.error("Error during consumption: %s", e)
                self.close_connection()
                logger.debug("Connection closed due to error, attempting to reconnect after %d seconds", self.connection.retry_delay)
                time.sleep(self.connection.retry_delay)

    def publish_message(self, exchange, routing_key, properties, body):
        # Adjusted the condition to check only for a missing routing_key
        if not routing_key:
            logger.error("Routing key is missing.")
            return

        max_retries = 3
        for attempt in range(max_retries):
            try:
                self.channel.basic_publish(
                    exchange=exchange,  # It's valid for this to be an empty string for the default exchange
                    routing_key=routing_key,
                    properties=properties,
                    body=body
                )
                logger.info("Message published to %s on attempt %d", routing_key, attempt + 1)
                break  # Exit the loop on success
            except pika.exceptions.AMQPError as e:
                logger.error("Failed to publish message on attempt %d due to AMQPError: %s", attempt + 1, e)
                if attempt < max_retries - 1:
                    logger.info("Retrying...")
                else:
                    logger.error("Failed to publish message after %d attempts", max_retries)
                # Handle the exception as needed, e.g., retrying, logging, or raising a custom exception