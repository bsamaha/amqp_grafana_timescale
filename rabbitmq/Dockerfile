FROM rabbitmq:3-management

# Copy the initialization script to the container
COPY init.sh /init.sh


RUN chmod +x /init.sh
CMD ["/bin/bash", "-c", "/init.sh & rabbitmq-server"]
