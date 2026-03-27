import grpc
import uuid
import datetime
from concurrent import futures
from typing import Dict

import sys
sys.path.append('weeks/week-07')
import service_pb2
import service_pb2_grpc


class ShipmentsServicer(service_pb2_grpc.ShipmentsServiceServicer):
    def __init__(self):
        self.shipments: Dict[str, dict] = {}
        self.counter = 1
    
    def CreateShipment(self, request, context):
        shipment_id = f"SHIP-{self.counter:04d}"
        self.counter += 1
        
        now = datetime.datetime.now().isoformat()
        
        shipment = {
            "id": shipment_id,
            "tracking_number": request.tracking_number,
            "status": "CREATED",
            "origin": request.origin,
            "destination": request.destination,
            "weight": request.weight,
            "created_at": now,
            "updated_at": now
        }
        
        self.shipments[shipment_id] = shipment
        
        return service_pb2.Shipment(
            id=shipment["id"],
            tracking_number=shipment["tracking_number"],
            status=shipment["status"],
            origin=shipment["origin"],
            destination=shipment["destination"],
            weight=shipment["weight"],
            created_at=shipment["created_at"],
            updated_at=shipment["updated_at"]
        )
    
    def GetShipment(self, request, context):
        shipment_id = request.id
        
        if shipment_id not in self.shipments:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Shipment with id '{shipment_id}' not found")
            return service_pb2.Shipment()
        
        shipment = self.shipments[shipment_id]
        
        return service_pb2.Shipment(
            id=shipment["id"],
            tracking_number=shipment["tracking_number"],
            status=shipment["status"],
            origin=shipment["origin"],
            destination=shipment["destination"],
            weight=shipment["weight"],
            created_at=shipment["created_at"],
            updated_at=shipment["updated_at"]
        )
    
    def ListShipments(self, request, context):
        shipments_list = list(self.shipments.values())
        
        # фильтрация по статусу
        if request.status:
            shipments_list = [s for s in shipments_list if s["status"] == request.status]
        
        total_count = len(shipments_list)
        
        # разделение на страницы
        page = request.page if request.page > 0 else 1
        page_size = request.page_size if request.page_size > 0 else 10
        
        start = (page - 1) * page_size
        end = start + page_size
        
        paginated_shipments = shipments_list[start:end]
        
        # конвертация в protobuf
        shipments_pb = []
        for s in paginated_shipments:
            shipments_pb.append(service_pb2.Shipment(
                id=s["id"],
                tracking_number=s["tracking_number"],
                status=s["status"],
                origin=s["origin"],
                destination=s["destination"],
                weight=s["weight"],
                created_at=s["created_at"],
                updated_at=s["updated_at"]
            ))
        
        return service_pb2.ListShipmentsResponse(
            shipments=shipments_pb,
            total_count=total_count,
            page=page,
            page_size=page_size
        )
    
    def UpdateShipmentStatus(self, request, context):
        shipment_id = request.id
        
        if shipment_id not in self.shipments:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Shipment with id '{shipment_id}' not found")
            return service_pb2.Shipment()
        
        shipment = self.shipments[shipment_id]
        shipment["status"] = request.status
        shipment["updated_at"] = datetime.datetime.now().isoformat()
        
        return service_pb2.Shipment(
            id=shipment["id"],
            tracking_number=shipment["tracking_number"],
            status=shipment["status"],
            origin=shipment["origin"],
            destination=shipment["destination"],
            weight=shipment["weight"],
            created_at=shipment["created_at"],
            updated_at=shipment["updated_at"]
        )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_ShipmentsServiceServicer_to_server(
        ShipmentsServicer(), server
    )
    server.add_insecure_port('[::]:50051')
    server.start()
    print("=" * 60)
    print("gRPC Сервер запущен")
    print("project_code: shipments-s01")
    print("Сервис: ShipmentsService")
    print("Порт: 50051")
    print("=" * 60)
    server.wait_for_termination()


if __name__ == '__main__':
    serve()