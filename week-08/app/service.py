import grpc
import uuid
import datetime
import time
import threading
from concurrent import futures
from typing import Dict, List, Generator

import sys
sys.path.append('weeks/week-08')
import service_pb2
import service_pb2_grpc


class ShipmentsServicer(service_pb2_grpc.ShipmentsServiceServicer):
    """
    Реализация gRPC сервиса с Server Streaming
    project_code: shipments-s01
    """
    
    def __init__(self):
        self.shipments: Dict[str, dict] = {}
        self.counter = 1
        self.shipment_updates: Dict[str, List[dict]] = {}  # История обновлений
    
    def CreateShipment(self, request, context):
        """Создание новой отправки"""
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
        
        # Инициализируем историю обновлений
        self.shipment_updates[shipment_id] = [
            {
                "status": "CREATED",
                "location": request.origin,
                "timestamp": now,
                "message": "Shipment created"
            }
        ]
        
        return service_pb2.Shipment(**shipment)
    
    def GetShipment(self, request, context):
        """Получение отправки по ID"""
        shipment_id = request.id
        
        if shipment_id not in self.shipments:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Shipment with id '{shipment_id}' not found")
            return service_pb2.Shipment()
        
        return service_pb2.Shipment(**self.shipments[shipment_id])
    
    def ListShipments(self, request, context):
        """Получение списка отправок"""
        shipments_list = list(self.shipments.values())
        
        if request.status:
            shipments_list = [s for s in shipments_list if s["status"] == request.status]
        
        total_count = len(shipments_list)
        page = request.page if request.page > 0 else 1
        page_size = request.page_size if request.page_size > 0 else 10
        
        start = (page - 1) * page_size
        end = start + page_size
        
        return service_pb2.ListShipmentsResponse(
            shipments=[service_pb2.Shipment(**s) for s in shipments_list[start:end]],
            total_count=total_count,
            page=page,
            page_size=page_size
        )
    
    def UpdateShipmentStatus(self, request, context):
        """Обновление статуса отправки"""
        shipment_id = request.id
        
        if shipment_id not in self.shipments:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return service_pb2.Shipment()
        
        shipment = self.shipments[shipment_id]
        old_status = shipment["status"]
        shipment["status"] = request.status
        shipment["updated_at"] = datetime.datetime.now().isoformat()
        
        # Добавляем обновление в историю
        self.shipment_updates[shipment_id].append({
            "status": request.status,
            "location": self._get_location_by_status(request.status),
            "timestamp": shipment["updated_at"],
            "message": f"Status changed from {old_status} to {request.status}"
        })
        
        return service_pb2.Shipment(**shipment)
    
    def TrackShipment(self, request, context):
        """
        Server Streaming метод для отслеживания статуса отправки
        Отправляет поток обновлений клиенту
        """
        shipment_id = request.shipment_id
        interval = request.update_interval_seconds if request.update_interval_seconds > 0 else 2
        max_updates = request.max_updates if request.max_updates > 0 else 10
        
        if shipment_id not in self.shipments:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Shipment '{shipment_id}' not found")
            return
        
        # Отправляем историю обновлений
        history = self.shipment_updates.get(shipment_id, [])
        for update in history[:max_updates]:
            yield service_pb2.ShipmentUpdate(
                shipment_id=shipment_id,
                status=update["status"],
                location=update["location"],
                timestamp=update["timestamp"],
                message=update["message"]
            )
            time.sleep(0.5)  # Небольшая задержка для имитации реального времени
        
        # Симулируем будущие обновления
        statuses = ["PICKED_UP", "IN_TRANSIT", "AT_SORTING_CENTER", "OUT_FOR_DELIVERY", "DELIVERED"]
        current_index = 0
        
        # Находим текущий статус
        for i, s in enumerate(statuses):
            if s == self.shipments[shipment_id]["status"]:
                current_index = i
                break
        
        updates_sent = len(history)
        
        # Отправляем следующие обновления
        for i in range(current_index + 1, len(statuses)):
            if updates_sent >= max_updates:
                break
            
            status = statuses[i]
            now = datetime.datetime.now().isoformat()
            
            yield service_pb2.ShipmentUpdate(
                shipment_id=shipment_id,
                status=status,
                location=self._get_location_by_status(status),
                timestamp=now,
                message=f"Shipment is now {status.lower()}"
            )
            
            updates_sent += 1
            time.sleep(interval)  # Ждем указанный интервал
        
        # Финальное сообщение
        if updates_sent < max_updates:
            yield service_pb2.ShipmentUpdate(
                shipment_id=shipment_id,
                status="COMPLETED",
                location=self.shipments[shipment_id]["destination"],
                timestamp=datetime.datetime.now().isoformat(),
                message="Tracking completed"
            )
    
    def _get_location_by_status(self, status: str) -> str:
        """Определяет локацию по статусу"""
        locations = {
            "CREATED": "Warehouse",
            "PICKED_UP": "Pickup point",
            "IN_TRANSIT": "Transit hub",
            "AT_SORTING_CENTER": "Sorting center",
            "OUT_FOR_DELIVERY": "Local depot",
            "DELIVERED": "Destination"
        }
        return locations.get(status, "Unknown")


def serve():
    """Запуск gRPC сервера"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_ShipmentsServiceServicer_to_server(
        ShipmentsServicer(), server
    )
    server.add_insecure_port('[::]:50051')
    server.start()
    print("=" * 60)
    print("gRPC Сервер с Server Streaming запущен")
    print("project_code: shipments-s01")
    print("Сервис: ShipmentsService")
    print("Порт: 50051")
    print("Streaming метод: TrackShipment")
    print("=" * 60)
    server.wait_for_termination()


if __name__ == '__main__':
    serve()