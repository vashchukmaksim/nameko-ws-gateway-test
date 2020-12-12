#!/bin/bash

# Check if rabbit is up and running before starting the service.
until nc -z ${RABBITMQ_HOST} ${RABBITMQ_PORT}; do
    echo "$(date) - waiting for rabbitmq on ${RABBITMQ_HOST}:${RABBITMQ_PORT}..."
    sleep 2
done

# Run Service
echo "Starting application..."
nameko run --config config.yaml src.service:WebSocketsGatewayService --backdoor 8000
