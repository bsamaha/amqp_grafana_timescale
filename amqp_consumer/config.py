import os


class Config:
    # PostgreSQL configuration
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "timescaledb")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "postgres")
    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")

    # RabbitMQ configuration
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
    RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "gnss_data_queue")
    RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
    RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")

    # Other configurations can be added here
