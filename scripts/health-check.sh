#!/bin/bash

echo "Checking BNG Telemetry Stack Health..."

# Check containers
echo "=== Container Status ==="
docker-compose ps

# Check InfluxDB
echo "=== InfluxDB Health ==="
curl -f http://localhost:8086/health || echo "InfluxDB not healthy"

# Check Grafana
echo "=== Grafana Health ==="
curl -f http://localhost:3000/api/health || echo "Grafana not healthy"

# Check BNG Simulator gNMI port
echo "=== BNG Simulator gNMI Port ==="
nc -z localhost 50051 && echo "gNMI port open" || echo "gNMI port closed"

# Check logs for errors
echo "=== Recent Errors ==="
docker-compose logs --tail=10 | grep -i error || echo "No recent errors found"