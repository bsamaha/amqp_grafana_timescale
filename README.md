# AMQP Consumer Project
The AMQP Consumer Project is designed to consume messages from RabbitMQ queues, process them, and interact with a PostgreSQL database for data persistence. This project is structured to run in a Docker environment, making it easy to deploy and scale.


![Sequence Flow](doc/simplified_flow.png)


## Components
- **RabbitMQ**: Message broker for receiving and sending messages.

- **TimescaleDB**: PostgreSQL-based database for storing processed data.

- **AMQP Consumer**: Python application that consumes messages from RabbitMQ, processes them, and stores the results in TimescaleDB.

- **Grafana**: Visualization tool for displaying data stored in TimescaleDB.


## Setup

### Prerequisites

- Docker and Docker Compose installed on your machine.


### Configuration

1. **Docker Compose**: The `docker-compose.yml` file defines the services, networks, and volumes for the project. It includes RabbitMQ, TimescaleDB, AMQP Consumer, and Grafana services.

2. **AMQP Consumer Dockerfile**: Located in `amqp_consumer/Dockerfile`, it defines the build process for the AMQP Consumer application, using a multi-stage build process for an efficient Docker image.


### Running the Project

1. **Start Services**: Run the following command in the root directory of the project to start all services defined in the `docker-compose.yml` file:
    `docker-compose up -d`


2. **Check Logs**: You can check the logs of the AMQP Consumer service to ensure it's running correctly:
    `docker-compose logs -f amqp_consumer`


## AMQP Consumer Application

### Main Components

- **`main.py`**: The entry point of the application. It initializes the database connection pool and starts consuming messages from RabbitMQ.

- **`rabbit_consumer.py`**: Defines the `RabbitConsumer` class for consuming messages from RabbitMQ and the `RabbitMQConnection` class for handling RabbitMQ connections.

- **`db_manager.py`**: Contains the `DBManager` class for managing database connections and performing CRUD operations on the PostgreSQL database.



### Environment Variables
The application uses environment variables for configuration, which are defined in the `amqp_consumer.env` file. These include database credentials, RabbitMQ credentials, and the log level.


### Health Checks
The `docker-compose.yml` file includes a health check for the AMQP Consumer service, ensuring the application is running and healthy.


## Grafana
Grafana is configured to visualize data from TimescaleDB. After starting the services, Grafana is accessible at `http://localhost:3000`. Default login credentials are `admin` for both username and password, which you should change immediately after the first login.


## Conclusion
The AMQP Consumer Project provides a robust solution for message processing with RabbitMQ and data persistence with TimescaleDB, all containerized for easy deployment and scalability.