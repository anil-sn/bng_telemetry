# Clean start
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d influxdb
sleep 30  # Wait for InfluxDB to initialize
docker-compose up -d bng-simulator
sleep 15  # Wait for simulator to start
docker-compose up -d telegraf grafana jupyter