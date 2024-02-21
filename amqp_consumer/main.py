from db.db_manager import DBManager
from rabbit_consumer import RabbitConsumer
import os
from logger import setup_logger
from message_processors.processor_factory import get_processor

# Setup logger for this module
logger = setup_logger(__name__, os.environ.get("LOG_LEVEL", "DEBUG"))

def start_consumer_in_thread():
    logger.debug("Starting consumer in a separate thread")
    try:
        # Use the wrapper function instead of a lambda for clarity
        rabbit_consumer = RabbitConsumer(get_processor)
        logger.debug("RabbitConsumer instance created")
        rabbit_consumer.setup_connection()  # Ensure connection is set up
        logger.info("RabbitMQ connection setup complete")
        rabbit_consumer.start_consuming()
    except Exception as e:
        logger.error("Exception in consumer thread: %s", e)
        raise

def main():
    logger.info("Application started")
    try:
        DBManager.initialize_connection_pool()
        logger.debug("Database connection pool initialized")
    except Exception as e:
        logger.error("Failed to initialize database connection pool: %s", e)
        return

    try:
        rabbit_consumer = RabbitConsumer(get_processor)
        rabbit_consumer.setup_connection()  # Ensure connection is set up
        rabbit_consumer.start_consuming()

    except Exception as e:
        logger.error("Failed to start consumer thread: %s", e)

if __name__ == "__main__":
    main()