#!/usr/bin/env python3
"""
BNG Telemetry Simulator
Generates synthetic subscriber telemetry data and serves it via gNMI.
"""

import time
import json
import random
import logging
from concurrent import futures
import threading
from datetime import datetime, timezone

import grpc
from pygnmi.server import gNMIServer
from pygnmi.proto import gnmi_pb2

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
NUM_SUBSCRIBERS = 50
GNMI_PORT = 50051
DATA_REFRESH_INTERVAL = 30  # seconds

class BNGTelemetrySimulator:
    def __init__(self):
        self.subscribers_data = {}
        self.data_lock = threading.Lock()
        self.running = False
        
    def generate_mac_address(self, index):
        """Generate a MAC address for subscriber"""
        return f"00:10:94:aa:{index:02x}:{random.randint(0, 255):02x}"
        
    def generate_subscriber_data(self, subscriber_id):
        """Generate telemetry data for a single subscriber"""
        mac = self.generate_mac_address(subscriber_id)
        
        # Base traffic with realistic patterns
        base_input = random.randint(1000000, 50000000)  # 1MB to 50MB
        base_output = int(base_input * random.uniform(0.1, 0.8))  # Typical asymmetric ratio
        
        return {
            "mac-address": mac,
            "s-vlan": random.randint(100, 4000),
            "c-vlan": random.randint(1, 4094),
            "interface-name": f"Bundle-Ether1.{subscriber_id}",
            "option82": f"option82-{subscriber_id}",
            "current-state": random.choice(["ACTIVE", "ACTIVE", "ACTIVE", "INACTIVE"]),  # 75% active
            "activation-timestamp": int(time.time()),
            "session-id": random.randint(10000, 99999),
            "ip-address": f"10.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}",
            "input-octets": base_input + random.randint(-1000000, 5000000),
            "output-octets": base_output + random.randint(-500000, 2000000),
            "input-packets": random.randint(1000, 10000),
            "output-packets": random.randint(500, 5000),
            "dhcp-discover": random.randint(0, 5),
            "dhcp-offer": random.randint(0, 5),
            "dhcp-request": random.randint(0, 10),
            "dhcp-ack": random.randint(0, 10),
            "radius-access-request": random.randint(0, 3),
            "radius-access-accept": random.randint(0, 3),
            "control-policy-id": random.randint(1000, 9999),
            "gx-enabled": random.choice([True, False]),
            "dynamic-policy-name": f"policy-{random.randint(1, 10)}"
        }
    
    def refresh_telemetry_data(self):
        """Periodically refresh the telemetry data"""
        while self.running:
            try:
                with self.data_lock:
                    for subscriber_id in range(1, NUM_SUBSCRIBERS + 1):
                        self.subscribers_data[subscriber_id] = self.generate_subscriber_data(subscriber_id)
                
                logger.info(f"Refreshed telemetry data for {NUM_SUBSCRIBERS} subscribers")
                time.sleep(DATA_REFRESH_INTERVAL)
                
            except Exception as e:
                logger.error(f"Error refreshing telemetry data: {e}")
                time.sleep(5)
    
    def get_gnmi_data(self):
        """Convert subscriber data to gNMI format"""
        with self.data_lock:
            gnmi_data = {
                "bng-telemetry": {
                    "subscribers": {
                        "subscriber": []
                    }
                }
            }
            
            for subscriber_id, data in self.subscribers_data.items():
                subscriber_entry = {
                    "mac-address": data["mac-address"],
                    "identity": {
                        "s-vlan": data["s-vlan"],
                        "c-vlan": data["c-vlan"],
                        "interface-name": data["interface-name"],
                        "option82": data["option82"]
                    },
                    "state": {
                        "current-state": data["current-state"],
                        "activation-timestamp": data["activation-timestamp"]
                    },
                    "sessions": {
                        "session": [{
                            "session-id": data["session-id"],
                            "ip-address": data["ip-address"]
                        }]
                    },
                    "statistics": {
                        "input-octets": data["input-octets"],
                        "output-octets": data["output-octets"],
                        "input-packets": data["input-packets"],
                        "output-packets": data["output-packets"],
                        "dhcp": {
                            "discover": data["dhcp-discover"],
                            "offer": data["dhcp-offer"],
                            "request": data["dhcp-request"],
                            "ack": data["dhcp-ack"]
                        },
                        "radius": {
                            "access-request": data["radius-access-request"],
                            "access-accept": data["radius-access-accept"]
                        }
                    },
                    "policies": {
                        "control-policy-id": data["control-policy-id"],
                        "gx-enabled": data["gx-enabled"],
                        "dynamic-policy-name": data["dynamic-policy-name"]
                    }
                }
                gnmi_data["bng-telemetry"]["subscribers"]["subscriber"].append(subscriber_entry)
            
            return gnmi_data
    
    def start(self):
        """Start the simulator"""
        self.running = True
        
        # Initialize data
        logger.info("Initializing subscriber telemetry data...")
        for subscriber_id in range(1, NUM_SUBSCRIBERS + 1):
            self.subscribers_data[subscriber_id] = self.generate_subscriber_data(subscriber_id)
        
        # Start data refresh thread
        refresh_thread = threading.Thread(target=self.refresh_telemetry_data)
        refresh_thread.daemon = True
        refresh_thread.start()
        
        # Start gNMI server
        logger.info(f"Starting gNMI server on port {GNMI_PORT}...")
        try:
            server = gNMIServer(
                port=GNMI_PORT,
                insecure=True,
                debug=True
            )
            
            # Set the data source
            server.set_config(self.get_gnmi_data)
            server.start_server()
            
            logger.info("gNMI server started successfully")
            
            # Keep the server running
            try:
                while True:
                    time.sleep(60)
                    # Update server data
                    server.set_config(self.get_gnmi_data)
                    
            except KeyboardInterrupt:
                logger.info("Shutting down...")
                
        except Exception as e:
            logger.error(f"Failed to start gNMI server: {e}")
            
        finally:
            self.running = False

if __name__ == "__main__":
    simulator = BNGTelemetrySimulator()
    simulator.start()