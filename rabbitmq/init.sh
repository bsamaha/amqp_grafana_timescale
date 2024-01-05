#!/bin/bash
sleep 10  # Wait for RabbitMQ server to start

# Declare the exchange, queue, and binding
rabbitmqadmin declare exchange name=gnss_data_exchange type=direct durable=true
rabbitmqadmin declare queue name=gnss_data_queue durable=true
rabbitmqadmin declare binding source=gnss_data_exchange destination=gnss_data_queue routing_key=gnss_routing_key

echo "Exchange, queue, and binding setup complete."