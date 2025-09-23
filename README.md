# bng_telemetry
A full-stack, open-source solution for streaming per-subscriber telemetry data from a BNG, collecting it in a time-series database, and applying machine learning for network analytics, anomaly detection, and predictive insights.

## Architecture Stack:

* **BNG (Broadband Network Gateway)**: Source of per-subscriber statistics
* **Telegraf**: gNMI client for telemetry collection
* **InfluxDB**: Time-series database for storing metrics
* **Grafana**: Visualization and dashboards
* **Jupyter Notebooks**: AI/ML analytics engine   

## Project Overview

This project provides a complete and modular pipeline for network telemetry and analytics, specifically designed for Broadband Network Gateways (BNGs). By leveraging modern streaming telemetry protocols (like gNMI over gRPC), we bypass traditional polling methods to capture high-volume, real-time, per-subscriber statistics. The collected data is then used to fuel AI and ML models for advanced network intelligence.

The key motivations for this project include:
* Proactive Network Management: Moving from reactive troubleshooting to proactive issue detection.
* Enhanced Subscriber Experience: Using AI/ML to identify performance degradation and service-affecting issues in real-time.
* Predictive Capacity Planning: Forecasting network traffic and resource utilization to optimize infrastructure investments.

## Architecture

The system is built on a modular, microservices-based architecture using popular open-source components.
* BNG: The source of per-subscriber statistics, configured to push data via gNMI.
* Telemetry Collector: Telegraf acts as the gNMI client, subscribing to telemetry streams from the BNG and forwarding data to the time-series database.
* Time-Series Database: InfluxDB is used for storing the high-volume, real-time telemetry metrics efficiently.
* Visualization: Grafana provides powerful dashboards for real-time monitoring and visualization of network and subscriber statistics.
* Analytics Engine: A Jupyter Notebook environment is used for running Python-based AI/ML analysis, querying data from InfluxDB, and developing models for insights like anomaly detection.

## Features

* Model-Driven Telemetry: Uses gNMI for efficient, event-based data streaming.
* Scalable Data Collection: Handles high-volume, high-frequency data streams from BNG devices.
* Real-time Monitoring: Offers dynamic dashboards for monitoring subscriber performance and network health.
* AI/ML Integration: Provides a framework for developing and deploying AI/ML models for network analytics.
* Containerized Deployment: Includes Docker Compose files for a quick and easy setup of the entire stack.
