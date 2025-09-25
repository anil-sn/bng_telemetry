# BNG Subscriber Telemetry and AI Analytics POC

## 1. Introduction

This document outlines the architecture of a Proof-of-Concept (POC) designed to demonstrate an end-to-end pipeline for real-time BNG (Broadband Network Gateway) subscriber telemetry. The system synthetically generates subscriber data, streams it using gNMI, stores it in a time-series database (TSDB), visualizes it on a Grafana dashboard, and applies machine learning techniques for anomaly detection.

The primary goal of this POC is to showcase how modern, open-source technologies can be integrated to build a powerful and scalable network analytics platform. This platform can provide network operators with deep insights into subscriber behavior, enabling proactive network monitoring, rapid troubleshooting, and intelligent capacity planning.

---

## 2. Architecture Overview

This POC is built on a modular, containerized stack of best-in-class open-source components. The architecture is designed to be scalable and flexible, allowing for easy substitution of components if needed.

The data flows through the system as follows:

1.  **Data Source**: A Python-based BNG Simulator generates realistic per-subscriber telemetry data and exposes it via a gNMI interface.
2.  **Collection**: Telegraf, configured with a gNMI input plugin, acts as a subscriber to the BNG Simulator's telemetry stream.
3.  **Storage**: Telegraf forwards the collected data to InfluxDB, which stores the time-series metrics efficiently.
4.  **Visualization**: Grafana connects to InfluxDB as a data source, enabling the creation of real-time dashboards for monitoring subscriber and network health.
5.  **Analytics**: A Jupyter Notebook environment provides the tools to query historical data from InfluxDB and apply AI/ML models for deeper analysis, such as anomaly detection and trend forecasting.

### Data Flow Diagram

```
[ BNG Simulator ] ----(gNMI over gRPC)----> [ Telegraf ] ----(Line Protocol)----> [ InfluxDB ]
      ^                                                                                ^
      |                                                                                |
(Python Script)                                                               (InfluxDB API)
                                                                                       |
                                                                                       |
+----------------------------------------+      +--------------------------------------+
|             Visualization              |      |           AI/ML Analytics            |
| [ Grafana ]<-----(Flux Query)----------+      | [ Jupyter Notebook ]<----(API Query)--+
+----------------------------------------+      +--------------------------------------+

```
```
bng_telemetry/
├── .env                  # Environment variables for InfluxDB credentials and config
├── .env.example          # Example environment file for users to copy
├── .gitignore            # Standard git ignore file for Python, Docker, etc.
├── README.md             # The main project documentation we've been writing
├── docker-compose.yml    # The master file to orchestrate all services
│
├── bng-simulator/
│   ├── Dockerfile        # Dockerfile to build the BNG simulator container
│   ├── requirements.txt  # Python dependencies (pygnmi, etc.)
│   └── simulator.py      # The Python script that generates data and runs the gNMI server
│
├── telegraf/
│   └── telegraf.conf     # Telegraf configuration for gNMI input and InfluxDB output
│
├── grafana/
│   ├── dashboards/       # Directory for dashboard JSON models
│   │   └── bng-dashboard.json
│   └── provisioning/
│       ├── dashboards.yml  # Grafana config to auto-load dashboards
│       └── datasources.yml # Grafana config to auto-provision the InfluxDB data source
│
└── jupyter/
    ├── Dockerfile        # Dockerfile to build the Jupyter Lab environment
    ├── requirements.txt  # Python dependencies for analytics (pandas, scikit-learn, etc.)
    └── notebooks/
        └── 1-Anomaly-Detection.ipynb # The sample notebook for ML analysis
```
---

## 3. Component Breakdown

This section provides a detailed look at each component in the technology stack and its specific role within this POC.

### 3.1. BNG Simulator (`bng-simulator`)

*   **Technology**: Python, `pygnmi`
*   **Role**: Acts as the data source for the entire pipeline. In a real-world deployment, this would be the actual BNG hardware or virtual appliance.
*   **Functionality**:
    *   **Data Generation**: A Python script synthetically generates a dynamic dataset for a predefined number of subscribers, including session states, IP addresses, and traffic counters (octets, packets).
    *   **gNMI Server**: It runs a `pygnmi` server instance, which loads the generated data and exposes it via a gN-MI interface. The data is periodically refreshed to simulate a live, changing network environment.
    *   **YANG-like Structure**: The data is structured hierarchically, mimicking a YANG model, with paths like `/bng-telemetry/subscribers/subscriber[mac=...]/state/`.

### 3.2. Telemetry Collector (`telegraf`)

*   **Technology**: Telegraf, `gnmi` input plugin
*   **Role**: Collects the streaming telemetry data from the BNG Simulator.
*   **Functionality**:
    *   **gNMI Subscription**: It is configured to establish a `STREAM` subscription to the BNG Simulator's gNMI server. This allows it to receive data updates in near real-time as they occur on the server.
    *   **Data Parsing**: It parses the incoming gNMI messages and transforms them into the InfluxDB Line Protocol format.
    *   **Data Forwarding**: It sends the formatted data to the InfluxDB instance for storage.

### 3.3. Time-Series Database (`influxdb`)

*   **Technology**: InfluxDB
*   **Role**: The central storage system for all telemetry data.
*   **Functionality**:
    *   **High-Performance Storage**: Optimized for storing and querying large volumes of time-stamped data with high throughput and efficiency.
    *   **Data Retention Policies**: Can be configured to automatically downsample or discard old data to manage storage usage.
    *   **Query Engine**: Provides the `Flux` query language, enabling powerful data retrieval, transformation, and analysis, which is used by both Grafana and the analytics engine.

### 3.4. Visualization Engine (`grafana`)

*   **Technology**: Grafana
*   **Role**: Provides a user-friendly interface for visualizing the telemetry data.
*   **Functionality**:
    *   **Data Source Integration**: Connects directly to InfluxDB to query the stored metrics.
    *   **Real-time Dashboards**: Enables the creation of dynamic dashboards with a variety of panels (graphs, gauges, tables, heatmaps) to monitor key performance indicators (KPIs) like active subscriber count, total bandwidth, and per-subscriber traffic.
    *   **Alerting**: Can be configured to trigger alerts based on predefined thresholds or conditions, providing proactive notifications of potential issues.

### 3.5. AI/ML Analytics Engine (`jupyter`)

*   **Technology**: Jupyter Notebook, Python, `pandas`, `scikit-learn`, `influxdb-client`
*   **Role**: The environment for offline data analysis, model training, and deriving advanced insights.
*   **Functionality**:
    *   **Data Exploration**: Allows data scientists and network engineers to query historical data from InfluxDB and perform exploratory data analysis (EDA).
    *   **Model Development**: Provides a platform to develop, train, and test machine learning models. For this POC, it includes a notebook for anomaly detection using the Isolation Forest algorithm.
    *   **Insight Generation**: The results of the analysis can be used to identify non-obvious patterns, forecast future trends, and detect subtle anomalies that simple threshold-based alerting might miss.

---

## 4. Setup and Deployment

This POC is fully containerized using Docker and Docker Compose, allowing for a quick and consistent setup across different environments.

### 4.1. Prerequisites

Before you begin, ensure you have the following software installed on your machine:

*   **Git**: For cloning the repository.
*   **Docker**: The containerization platform.
*   **Docker Compose**: For orchestrating the multi-container application.

### 4.2. Installation Steps

1.  **Clone the Repository**

    Open your terminal and clone the project repository from GitHub:
    ```bash
    git clone https://github.com/anil-sn/bng_telemetry.git
    cd bng_telemetry
    ```

2.  **Configure Environment Variables**

    The configuration for InfluxDB (like username, password, and initial bucket) is managed through an environment file.

    Copy the example file to create your own local configuration:
    ```bash
    cp .env.example .env
    ```
    You can review the settings in the `.env` file. For this POC, the default values are sufficient to get started.

3.  **Launch the Stack**

    Bring up the entire application stack using Docker Compose. This command will build the necessary images and start all the services in the background.
    ```bash
    docker-compose up -d
    ```

4.  **Verify the Services**

    Check that all containers are running correctly:
    ```bash
    docker-compose ps
    ```
    You should see `bng-simulator`, `telegraf`, `influxdb`, `grafana`, and `jupyter` listed with a "running" or "up" state.

    You can now access the web interfaces for the various services:

    *   **Grafana**: [http://localhost:3000](http://localhost:3000)
        *   Login with the default credentials: `admin` / `admin`. You will be prompted to change the password on your first login.
    *   **InfluxDB UI**: [http://localhost:8086](http://localhost:8086)
        *   Use the credentials defined in your `.env` file to log in and explore the raw data.
    *   **Jupyter Notebook**: [http://localhost:8888](http://localhost:8888)
        *   You will need a token to log in for the first time. Get it by checking the logs of the Jupyter container:
          ```bash
          docker-compose logs jupyter
          ```
          Look for a URL containing the token, like `http://127.0.0.1:8888/?token=...`. Copy the token value into the login page. 
Of course. Here is the next section, which guides you through using the running services to see the telemetry data and run the analytics.

---

## 5. Usage and Demonstration

Once the stack is running, you can explore the various components to see the end-to-end data flow and analytics in action.

### 5.1. Visualizing Telemetry in Grafana

The Grafana service is pre-configured with a connection to the InfluxDB data source and a pre-built dashboard for BNG subscriber monitoring.

1.  **Access Grafana**: Open your web browser and navigate to [http://localhost:3000](http://localhost:3000).
2.  **Login**: Use the default credentials (`admin`/`admin`) and change the password when prompted.
3.  **Open the Dashboard**:
    *   On the left-hand menu, click on the **Dashboards** icon.
    *   Click on the **"BNG Subscriber Monitoring"** dashboard.

You will see several panels visualizing the data streamed from the BNG Simulator in near real-time:

*   **Active Subscribers**: A gauge showing the current count of active subscribers.
*   **Total Bandwidth (Input/Output)**: A time-series graph displaying the aggregate ingress and egress traffic across all subscribers.
*   **Per-Subscriber Input Octets**: A table view that lists each subscriber and their current traffic volume, allowing you to identify the top talkers.
*   **DHCP and RADIUS Statistics**: Graphs showing the rates of key protocol messages, which can be useful for monitoring control plane health.

The dashboard should update automatically as the BNG Simulator generates new data.

### 5.2. Running AI/ML Analytics in Jupyter

The Jupyter environment is set up with a sample notebook to perform anomaly detection on the collected traffic data.

1.  **Access JupyterLab**: Open your browser and go to [http://localhost:8888](http://localhost:8888).
2.  **Login**: Use the token from the `docker-compose logs jupyter` command as described in the setup section.
3.  **Open the Notebook**:
    *   In the file browser on the left, navigate into the `notebooks` directory.
    *   Double-click on the `1-Anomaly-Detection.ipynb` file to open it.
4.  **Run the Analysis**:
    *   The notebook contains a series of cells with Python code and explanations.
    *   You can run each cell sequentially by clicking on it and pressing **Shift + Enter**.
    *   The notebook will:
        1.  Establish a connection to the InfluxDB database.
        2.  Query the traffic data (`input_octets`) for the last hour.
        3.  Use the **Isolation Forest** algorithm from `scikit-learn` to identify subscribers whose traffic patterns deviate significantly from the norm.
        4.  Print a list of MAC addresses for the subscribers that have been flagged as anomalies.

This demonstration showcases how the stored telemetry data can be leveraged for more advanced, offline analysis to uncover insights that may not be apparent from real-time visualization alone.

---

## 6. Customization and Extension

This POC is designed to be a flexible foundation. You can easily modify various parts of the system to simulate different scenarios or integrate new functionalities.

### 6.1. Adjusting the BNG Simulator

The core of the simulation is the `bng-simulator/generator.py` script. You can edit this file to change the behavior of the synthetic data generation.

*   **Number of Subscribers**: To change the number of simulated subscribers, modify the `NUM_SUBSCRIBERS` variable at the top of the script.
    ```python
    # In bng-simulator/generator.py
    NUM_SUBSCRIBERS = 50  # Change this value to 100, 500, etc.
    ```
*   **Data Generation Logic**: You can alter the `generate_subscriber_data` function to introduce different data patterns. For example, you could simulate traffic spikes, session flaps (changing the `current_state`), or different DHCP message rates.
*   **Adding New Metrics**: To add a new telemetry metric:
    1.  Add the new key-value pair to the subscriber dictionary within the `generate_subscriber_data` function.
    2.  Ensure your Telegraf configuration (`telegraf/telegraf.conf`) is updated to process and store this new field if necessary.

After making changes to the Python script, you will need to restart the simulator container to apply them:
```bash
docker-compose restart bng-simulator
```

### 6.2. Modifying Telegraf Configuration

The data collection process is defined in `telegraf/telegraf.conf`. You can edit this file to:

*   **Change the Subscription Path**: Modify the `subscription` block in the `[[inputs.gnmi]]` section to subscribe to a different data path or add more paths.
*   **Add Data Processors**: Telegraf has a wide range of processor plugins that can be used to enrich, filter, or transform data before it is sent to InfluxDB.
*   **Change the Output**: You can replace or add to the `[[outputs.influxdb_v2]]` section to send data to other destinations, such as Kafka, Prometheus, or another database.

Remember to restart the Telegraf container after modifying its configuration:
```bash
docker-compose restart telegraf
```

### 6.3. Developing New AI/ML Models

The `jupyter/notebooks/` directory is the ideal place to develop new analytics. You can create new `.ipynb` files to:

*   **Forecast Traffic**: Use time-series forecasting models (like ARIMA or Prophet) to predict future bandwidth needs.
*   **Classify Subscriber Behavior**: Develop clustering models (like K-Means) to group subscribers into different profiles based on their data usage patterns.
*   **Train Anomaly Detectors**: Experiment with other anomaly detection algorithms beyond Isolation Forest to see which performs best for your simulated data.

---

## 7. Future Enhancements

This POC provides a solid foundation, but there are numerous avenues for future development and enhancement to make it more robust, realistic, and feature-rich.

### 7.1. Enhanced BNG Simulator Realism

*   **Dynamic Subscriber Lifecycle**: Implement more complex subscriber lifecycle events, such as dynamic session creation/deletion, DHCP lease expirations, and RADIUS re-authentications that trigger state changes and specific event logs.
*   **Realistic Traffic Patterns**: Incorporate more sophisticated traffic generation models that mimic real-world subscriber usage, including bursty traffic, video streaming patterns, and idle periods, perhaps leveraging distributions like Pareto or Poisson.
*   **Multi-BNG Simulation**: Extend the simulator to mimic multiple BNG instances, each generating data, to test the scalability of the collection and storage layers.
*   **Configurable YANG Model**: Allow the simulator to load a YANG model dynamically, enabling easier alignment with specific vendor models.

### 7.2. Advanced Telemetry Collection

*   **Multi-Path Subscriptions**: Implement more complex gNMI subscription logic in Telegraf, including conditional subscriptions or subscriptions to specific sub-paths based on subscriber type or service.
*   **Error Handling and Retries**: Enhance Telegraf's configuration for robust error handling and retry mechanisms in case of network issues or temporary unavailability of the BNG Simulator or InfluxDB.
*   **Integration with Real BNGs**: Develop specific integration guides and configuration templates for connecting Telegraf to actual vendor BNG devices that support gNMI.

### 7.3. Enhanced Storage and Scalability

*   **Clustered InfluxDB**: For high-volume scenarios, explore setting up a clustered InfluxDB (e.g., InfluxDB Enterprise or using a cloud-managed service) to handle increased data ingestion and query loads.
*   **Data Aggregation and Downsampling**: Implement automatic downsampling policies within InfluxDB or via Telegraf processors to reduce storage footprint for older data while retaining long-term trends.
*   **Alternative TSDBs**: Investigate integration with other time-series databases like Prometheus, TimescaleDB (PostgreSQL extension), or OpenTSDB, particularly if the use case requires different query capabilities or existing infrastructure.

### 7.4. Advanced Visualization and Alerting

*   **Interactive Drill-Down Dashboards**: Create more hierarchical Grafana dashboards allowing users to drill down from an aggregate network view to individual subscriber performance.
*   **Predictive Alerts**: Integrate machine learning models directly into Grafana's alerting system to trigger alerts based on predicted anomalies or deviations from forecasted trends, rather than just static thresholds.
*   **Custom Grafana Plugins**: Develop custom Grafana plugins for specialized BNG-specific visualizations or data interactions.

### 7.5. Sophisticated AI/ML Analytics

*   **Real-time Anomaly Detection**: Implement a separate service (e.g., a Python microservice) that continuously queries InfluxDB for new data, runs anomaly detection models in near real-time, and pushes alerts to Grafana or a notification system.
*   **Root Cause Analysis**: Develop models that attempt to correlate anomalies with potential root causes, such as changes in RADIUS authentication success rates, DHCP lease failures, or specific policy updates.
*   **Reinforcement Learning for Network Optimization**: Explore how reinforcement learning could be applied to dynamically adjust network parameters (e.g., QoS policies, load balancing) based on real-time subscriber experience and resource utilization.
*   **Data Quality Monitoring**: Implement ML models to monitor the quality and integrity of the incoming telemetry data itself, detecting missing values, sudden drops in data rates, or unexpected data types.

### 7.6. Security Enhancements

*   **TLS/SSL for gNMI and gRPC**: Implement TLS for secure communication between the BNG Simulator/Telegraf and Telegraf/InfluxDB.
*   **Authentication and Authorization**: Configure proper authentication (e.g., client certificates for gNMI, API tokens for InfluxDB and Grafana) and authorization mechanisms for all components.

These enhancements would further mature the POC into a robust, production-ready solution for managing and optimizing BNG networks.

---

## 8. Usage and Demonstration

Once the stack is running, you can explore the various components to see the end-to-end data flow and analytics in action.

### 8.1. Visualizing Telemetry in Grafana

The Grafana service is pre-configured with a connection to the InfluxDB data source and a pre-built dashboard for BNG subscriber monitoring.

1.  **Access Grafana**: Open your web browser and navigate to [http://localhost:3000](http://localhost:3000).
2.  **Login**: Use the default credentials (`admin`/`admin`) and change the password when prompted.
3.  **Open the Dashboard**:
    *   On the left-hand menu, click on the **Dashboards** icon.
    *   Click on the **"BNG Subscriber Monitoring"** dashboard.

You will see several panels visualizing the data streamed from the BNG Simulator in near real-time:

*   **Active Subscribers**: A gauge showing the current count of active subscribers.
*   **Total Bandwidth (Input/Output)**: A time-series graph displaying the aggregate ingress and egress traffic across all subscribers.
*   **Top Subscribers by Input Traffic**: A table view that lists each subscriber and their total traffic volume in the selected time range, allowing you to identify the top talkers.

The dashboard should update automatically as the BNG Simulator generates new data.

### 8.2. Running AI/ML Analytics in Jupyter

The Jupyter environment is set up with a sample notebook to perform anomaly detection on the collected traffic data.

1.  **Access JupyterLab**: Open your browser and go to [http://localhost:8888](http://localhost:8888).
2.  **Login**: You will need a token to log in for the first time. Get it by checking the logs of the Jupyter container:
    ```bash
    docker-compose logs jupyter
    ```
    Look for a URL in the logs containing the token, like `http://127.0.0.1:8888/lab?token=...`. Copy the full URL into your browser, or just the token value into the login page.

3.  **Open the Notebook**:
    *   In the file browser on the left, double-click on the `1-Anomaly-Detection.ipynb` file to open it.
4.  **Run the Analysis**:
    *   The notebook contains a series of cells with Python code and explanations.
    *   You can run each cell sequentially by clicking on it and pressing **Shift + Enter**.
    *   The notebook will:
        1.  Establish a connection to the InfluxDB database.
        2.  Query the traffic data (`input_octets`) for the last hour.
        3.  Use the **Isolation Forest** algorithm from `scikit-learn` to identify subscribers whose traffic patterns deviate significantly from the norm.
        4.  Print a list of MAC addresses for the subscribers that have been flagged as anomalous.

This demonstration showcases how the stored telemetry data can be leveraged for more advanced, offline analysis to uncover insights that may not be apparent from real-time visualization alone.

Of course. A troubleshooting guide is an essential part of any good `README`. Here is a section covering common issues and their solutions.

---

## 9. Troubleshooting

If you encounter issues while running the POC, here are some common problems and how to resolve them.

### 9.1. General Commands

*   **Check container status**: To see which services are running, stopped, or have errors.
    ```bash
    docker-compose ps
    ```
*   **View logs for a specific service**: This is the most important step for debugging. Replace `<service_name>` with `telegraf`, `bng-simulator`, `influxdb`, etc.
    ```bash
    docker-compose logs <service_name>
    ```
*   **Follow logs in real-time**:
    ```bash
    docker-compose logs -f <service_name>
    ```

### 9.2. Issue: No data in Grafana dashboards

If your dashboards are empty or show "No Data":

1.  **Check Telegraf Logs**: This is the most likely place to find the issue.
    ```bash
    docker-compose logs telegraf
    ```
    *   Look for errors connecting to the `bng-simulator` (e.g., `connection refused`). This means the simulator might not be running correctly.
    *   Look for errors connecting to `influxdb` (e.g., `unauthorized`). This could be a token or configuration mismatch.
    *   If there are no errors, Telegraf might not be parsing the data correctly. Check that the `[[inputs.gnmi.json_v2]]` section in `telegraf.conf` matches the data structure in `simulator.py`.

2.  **Check BNG Simulator Logs**: Ensure the simulator started correctly and is generating data.
    ```bash
    docker-compose logs bng-simulator
    ```
    You should see log messages like "Refreshing telemetry data..." and "gNMI server starting...".

3.  **Check InfluxDB Manually**:
    *   Go to the InfluxDB UI at [http://localhost:8086](http://localhost:8086).
    *   Login with the credentials from your `.env` file.
    *   On the left menu, go to **Explore** (or **Data Explorer**).
    *   In the query builder, select the `bng-bucket`, the `bng_subscriber_stats` measurement, and a field like `input_octets`.
    *   If you see data here, the problem is with Grafana. If you don't, the problem is with Telegraf or the simulator.

### 9.3. Issue: Jupyter Notebook cannot connect to InfluxDB

If you get a connection error when running the cells in the `1-Anomaly-Detection.ipynb` notebook:

1.  **Verify InfluxDB is Running**: Run `docker-compose ps` and ensure the `influxdb` container is `Up`.
2.  **Check Environment Variables**: The notebook connects using environment variables passed to the Jupyter container. Check the `environment` section for the `jupyter` service in your `docker-compose.yml` file and ensure the variable names match what's used in the notebook's first code cell.

### 9.4. How to Reset the Entire Stack

If you want to start completely fresh, clearing all stored data in InfluxDB and Grafana:

1.  **Stop and Remove Containers**: The `-v` flag is crucial as it also removes the Docker volumes where the data is stored.
    ```bash
    docker-compose down -v
    ```
2.  **Relaunch the Stack**:
    ```bash
    docker-compose up -d
    ```

## Additional Information

### 1. Understanding gNMI, gRPC, and YANG 

To effectively model your BNG subscriber data, it's essential to understand the roles of gNMI, gRPC, and YANG: 

*   **gRPC (gRPC Remote Procedure Calls)**: A modern, open-source, high-performance RPC framework that can run in any environment. It is the foundation for gNMI, providing a robust and efficient transport mechanism. 
*   **YANG (Yet Another Next Generation)**: A data modeling language used to model configuration and state data of network elements. YANG is used to create a structured, predictable, and vendor-neutral representation of the data you want to stream. 
*   **gNMI (gRPC Network Management Interface)**: An open-source protocol for network management and streaming telemetry from network devices. It uses gRPC for transport and YANG for data modeling. gNMI is particularly well-suited for AI analytics due to its efficiency and ability to stream data in near real-time. 

### 2. Proposed YANG Model for BNG Subscriber Data 

Below is a proposed hierarchical structure for a YANG model based on the provided subscriber information. This model organizes the data into logical groups, making it easier to query and analyze. 

**Top-Level Container:** `bng-subscriber-telemetry` 

This container will hold all the subscriber-related telemetry data. 

**Subscriber List:** `subscribers` 

This is a list of all subscribers, keyed by their MAC address for unique identification. 

```
/bng-subscriber-telemetry
  /subscribers
    /subscriber[mac-address='...'] 
```

**Within each subscriber entry, the data is further broken down into the following containers:** 

*   **/identity**: Contains static identification information for the subscriber. 
    *   `mac-address` (string) 
    *   `s-vlan` (uint16) 
    *   `c-vlan` (uint16) 
    *   `interface-name` (string) 
    *   `option82` (string) 
*   **/state**: Reflects the current operational state of the subscriber. 
    *   `current-state` (enumeration: ACTIVE, INACTIVE, etc.) 
    *   `activation-timestamp` (timestamp) 
*   **/sessions**: A list of IP sessions associated with the subscriber, keyed by session ID. 
    *   `session[session-id='...']` 
        *   `session-id` (uint64) 
        *   `session-state` (enumeration: ACTIVE, INACTIVE, etc.) 
        *   `ip-address-family` (identity: ipv4, ipv6) 
        *   `ip-address` (inet:ip-address) 
        *   `prefix` (inet:ip-prefix) 
        *   `subnet-mask` (inet:ip-address) 
        *   `default-gateway` (inet:ip-address) 
        *   `lease-time` (uint32) 
        *   `allocation-timestamp` (timestamp) 
*   **/policies**: Details about policies applied to the subscriber. 
    *   `control-policy-id` (uint32) 
    *   `gx-enabled` (boolean) 
    *   `dynamic-policy-name` (string) 
*   **/statistics**: A comprehensive set of counters for various protocols and events. This is highly valuable for anomaly detection and trend analysis. 
    *   `/dhcpv4` 
    *   `/dhcpv6` 
    *   `/radius-authentication` 
    *   `/radius-accounting` 
    *   `/session-activation` 
    *   `/hardware-counters` 
*   **/event-history**: A log of significant events in the subscriber's lifecycle. 
    *   `event[timestamp='...']` 
        *   `timestamp` (timestamp) 
        *   `graph-name` (string) 
        *   `event-name` (string) 
        *   `current-state` (string) 

### 3. Streaming Data with gNMI for AI Analytics 

With a YANG model in place, you can use gNMI to stream the data to your AI analytics platform. gNMI offers several subscription modes, with `STREAM` being the most powerful for continuous monitoring: 

*   **`STREAM` Subscriptions**: This mode allows for continuous data streaming and has two sub-modes: 
    *   **`SAMPLE`**: Data is streamed at a specified interval (e.g., every 30 seconds). This is ideal for collecting time-series data like traffic counters for trend analysis and forecasting. 
    *   **`ON_CHANGE`**: Data is streamed only when a value changes. This is highly efficient for monitoring state changes, such as subscriber session state transitions or policy updates, which can be critical inputs for real-time anomaly detection. 

**Example gNMI Subscriptions:** 

*   **To monitor session state changes for all subscribers in real-time:** 
    *   **Path**: `/bng-subscriber-telemetry/subscribers/subscriber/sessions/session/session-state` 
    *   **Mode**: `STREAM` 
    *   **Sub-mode**: `ON_CHANGE` 
*   **To sample DHCP statistics every minute for a specific subscriber:** 
    *   **Path**: `/bng-subscriber-telemetry/subscribers/subscriber[mac-address='00:10:94:aa:00:01']/statistics/dhcpv4` 
    *   **Mode**: `STREAM` 
    *   **Sub-mode**: `SAMPLE` 
    *   **Interval**: 60 seconds 

### 4. Vendor Documentation and Industry Standards 

While this model is a robust starting point based on your provided data, it's highly recommended to consult vendor-specific documentation for their YANG models. Additionally, standards bodies like the **Broadband Forum (BBF)** and **OpenConfig** offer standardized YANG models for BNG and subscriber management. Aligning with these standards will ensure greater interoperability and a more comprehensive set of telemetry data. 

By modeling your BNG subscriber data with YANG and streaming it via gNMI, you can create a powerful data pipeline to fuel your AI analytics, enabling proactive network monitoring, anomaly detection, and capacity planning.