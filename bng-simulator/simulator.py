import logging
import time
import random
import grpc
from concurrent import futures
from google.protobuf import empty_pb2
from gnmi_pb2 import Path, PathElem, Update, Notification, SubscribeResponse
import gnmi_pb2_grpc

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('simulator.log'),
        logging.StreamHandler()
    ]
)

class BNGSimulatorServicer(gnmi_pb2_grpc.gNMI):
    def __init__(self):
        self.subscribers = [f"sub-{i}" for i in range(1, 1001)]  # 1000 subscribers
        logging.info("Initialized BNG simulator with %d subscribers", len(self.subscribers))

    def Subscribe(self, request_iterator, context):
        logging.debug("Received subscription request")
        try:
            for request in request_iterator:
                for sub in request.subscribe.subscription:
                    path = sub.path
                    logging.debug(f"Processing subscription for path: {path}")
                    while not context.is_active():
                        logging.warning("Client disconnected, stopping stream")
                        return
                    while True:
                        updates = []
                        for subscriber in self.subscribers:
                            # Simulate telemetry data
                            data = {
                                "uptime": random.randint(60, 86400),
                                "bytes_in": random.randint(1000, 1000000),
                                "bytes_out": random.randint(1000, 1000000),
                                "errors": random.randint(0, 10)
                            }
                            for key, value in data.items():
                                path_elem = Path(elem=[
                                    PathElem(name="bng"),
                                    PathElem(name="subscribers"),
                                    PathElem(name=subscriber),
                                    PathElem(name=key)
                                ])
                                update = Update(
                                    path=path_elem,
                                    val=gnmi_pb2.TypedValue(int_val=value)
                                )
                                updates.append(update)
                        notification = Notification(
                            timestamp=int(time.time() * 1000),
                            update=updates
                        )
                        response = SubscribeResponse(update=notification)
                        logging.debug("Sending telemetry update for %d subscribers", len(self.subscribers))
                        yield response
                        time.sleep(5)  # Stream every 5 seconds
        except Exception as e:
            logging.error(f"Subscription error: {str(e)}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            raise

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    gnmi_pb2_grpc.add_gNMIServicer_to_server(BNGSimulatorServicer(), server)
    server.add_insecure_port('[::]:50051')
    logging.info("Starting gNMI server on port 50051")
    try:
        server.start()
        server.wait_for_termination()
    except Exception as e:
        logging.error(f"Server error: {str(e)}", exc_info=True)
        raise

if __name__ == '__main__':
    logging.info("BNG Simulator starting...")
    try:
        serve()
    except KeyboardInterrupt:
        logging.info("Shutting down simulator")
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}", exc_info=True)