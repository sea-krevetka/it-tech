from locust import HttpUser, task, between, tag
import grpc
import shipments_pb2
import shipments_pb2_grpc

class RESTUser(HttpUser):
    wait_time = between(0.5, 2)
    
    @task(3)
    def list_shipments(self):
        self.client.get("/api/shipments")
    
    @task(1)
    def get_shipment(self):
        self.client.get("/api/shipments/1")
    
    @task(1)
    def create_shipment(self):
        self.client.post("/api/shipments", json={
            "tracking_number": "TEST-001",
            "origin": "Moscow",
            "destination": "SPB",
            "weight": 5.5
        })


class GRPCUser(grpc.User):
    wait_time = between(0.5, 2)
    
    def on_start(self):
        self.channel = grpc.insecure_channel('localhost:50051')
        self.stub = shipments_pb2_grpc.ShipmentsServiceStub(self.channel)
    
    @task(3)
    def list_shipments(self):
        self.stub.ListShipments(shipments_pb2.ListShipmentsRequest(page=1, page_size=10))
    
    @task(1)
    def create_shipment(self):
        self.stub.CreateShipment(shipments_pb2.CreateShipmentRequest(
            tracking_number="TEST-001",
            origin="Moscow",
            destination="SPB",
            weight=5.5
        ))