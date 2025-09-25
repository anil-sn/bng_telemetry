import time
import random
import json
import logging
import threading
from faker import Faker

from pygnmi.server import GnmiServer, GrpcServer

# --- Configuration Constants ---
NUM_SUBSCRIBERS = 50
REFRESH_INTERVAL = 10  # seconds
GNMI_HOST = '0.0.0.0'
GNMI_PORT = 50051

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
fake = Faker()

# In-memory store for our telemetry data
# We use a dictionary to store previous counter values for realistic increments
telemetry_store = {
    "subscribers": []
}

def initialize_subscribers():
    """Generates the initial static data for all subscribers."""
    subs = []
    for i in range(NUM_SUBSCRIBERS):
        mac = fake.mac_address()
        subs.append({
            "mac": mac,
            "identity": {
                "mac-address": mac,
                "s-vlan": random.randint(100, 4000),
                "c-vlan": random.randint(1, 100),
                "interface-name": f"1/1/x{random.randint(1, 4)}",
                "option82": f"sub-identity-{i+1}"
            },
            # --- Dynamic data will be populated by the update function ---
            "state": {},
            "sessions": {
                "ipv4": {},
                "ipv6": {}
            },
            "statistics": {
                "dhcpv4": {"rx_request": 0, "tx_ack": 0, "rx_release": 0},
                "dhcpv6": {"tx_reply": 0, "rx_renew": 0, "rx_release": 0},
                "radius": {"tx_auth_request": 0, "rx_auth_success": 0, "tx_interim_request": 0},
                "hardware": {"input_octets": 0, "output_octets": 0}
            }
        })
    telemetry_store["subscribers"] = subs
    logging.info(f"Initialized {len(subs)} subscribers.")


def update_telemetry_data():
    """
    Updates the dynamic parts of the telemetry data for all subscribers.
    This function simulates real-time changes in the network.
    """
    global telemetry_store
    logging.info("Refreshing telemetry data...")

    for sub in telemetry_store["subscribers"]:
        # --- Update State ---
        is_active = random.random() > 0.05  # 95% chance of being active
        sub["state"]["current-state"] = "ACTIVE" if is_active else "INACTIVE"
        sub["state"]["activation-timestamp"] = int(time.time()) - random.randint(3600, 86400)

        # --- Update Sessions (only if active) ---
        if is_active:
            sub["sessions"]["ipv4"] = {
                "session-state": "IP_SESSION_ACTIVE",
                "ip-address": fake.ipv4(),
                "lease-time": 9000
            }
            sub["sessions"]["ipv6"] = {
                "session-state": "IP_SESSION_ACTIVE",
                "ip-address": fake.ipv6(),
                "prefix": f"{fake.ipv6_network()}/64"
            }
        else:
             sub["sessions"]["ipv4"] = {"session-state": "IP_SESSION_INACTIVE"}
             sub["sessions"]["ipv6"] = {"session-state": "IP_SESSION_INACTIVE"}


        # --- Update Statistics (counters always increase) ---
        stats = sub["statistics"]
        if is_active:
            stats["dhcpv4"]["rx_request"] += random.randint(0, 5)
            stats["dhcpv4"]["tx_ack"] = stats["dhcpv4"]["rx_request"] # ACK matches request
            stats["radius"]["tx_auth_request"] += 1
            stats["radius"]["rx_auth_success"] += 1 if random.random() > 0.01 else 0
            stats["radius"]["tx_interim_request"] += random.randint(1, 3)
            stats["hardware"]["input_octets"] += random.randint(100000, 5000000)
            stats["hardware"]["output_octets"] += random.randint(50000, 1000000)
        else:
             # If inactive, maybe a release message is sent
             stats["dhcpv4"]["rx_release"] += 1


def telemetry_update_worker():
    """A worker function to run in a background thread, updating data."""
    while True:
        update_telemetry_data()
        time.sleep(REFRESH_INTERVAL)


class GnmiBngServer(GnmiServer):
    def __init__(self, grpc_server):
        super().__init__(grpc_server, "bng-telemetry")

    def sub_telemetry(self, path, req):
        """
        A simple handler to return the entire telemetry tree.
        In a real implementation, this would parse the path and return specific elements.
        """
        logging.info(f"Received telemetry request for path: {path}")
        # For this POC, we return the whole tree regardless of the path.
        # This is sufficient for Telegraf to query and parse.
        # The structure of `telemetry_store` is what Telegraf will see.
        return json.dumps(telemetry_store)


if __name__ == '__main__':
    # 1. Initialize the subscriber base data
    initialize_subscribers()

    # 2. Start the background thread to periodically update the dynamic data
    update_thread = threading.Thread(target=telemetry_update_worker, daemon=True)
    update_thread.start()
    logging.info(f"Started background telemetry update worker (interval: {REFRESH_INTERVAL}s)")

    # 3. Setup and start the gNMI server
    grpc_server = GrpcServer(f"{GNMI_HOST}:{GNMI_PORT}")
    gnmi_server = GnmiBngServer(grpc_server)
    logging.info(f"gNMI server starting on {GNMI_HOST}:{GNMI_PORT}")
    grpc_server.start()

    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Shutting down gNMI server.")
        grpc_server.stop(0)