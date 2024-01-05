FROM rabbitmq:3-management

# Copy the initialization script to the container
COPY init.sh /init.sh


# Set the default command to execute the script after RabbitMQ starts
CMD ["/bin/bash", "-c", "/init.sh & rabbitmq-server", "chmod", "+x", "/init.sh"]