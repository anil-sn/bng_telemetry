#!/bin/bash
set -e

# Wait for InfluxDB to be ready
until curl -s http://localhost:8086/ping; do
  echo "Waiting for InfluxDB..."
  sleep 5
done

# Setup using influx CLI
influx setup --username "${DOCKER_INFLUXDB_INIT_USERNAME}" \
  --password "${DOCKER_INFLUXDB_INIT_PASSWORD}" \
  --org "${DOCKER_INFLUXDB_INIT_ORG}" \
  --bucket "${DOCKER_INFLUXDB_INIT_BUCKET}" \
  --token "${DOCKER_INFLUXDB_INIT_ADMIN_TOKEN}" \
  --force

# Additional logging
echo "InfluxDB initialized with org: ${DOCKER_INFLUXDB_INIT_ORG}, bucket: ${DOCKER_INFLUXDB_INIT_BUCKET}"