import grpc
import sys
sys.path.append('weeks/week-07')
import service_pb2
import service_pb2_grpc


def run():
    channel = grpc.insecure_channel('localhost:50051')
    stub = service_pb2_grpc.ShipmentsServiceStub(channel)
    
    print("=" * 60)
    print("gRPC Клиент для ShipmentsService")
    print("project_code: shipments-s01")
    print("=" * 60)
    
    print("\n1. Создаем новую отправку...")
    shipment = stub.CreateShipment(
        service_pb2.CreateShipmentRequest(
            tracking_number="TRK-001",
            origin="Moscow",
            destination="Saint Petersburg",
            weight=5.5
        )
    )
    print(f"   Создана: {shipment}")
    shipment_id = shipment.id
    
    print(f"\n2. Получаем отправку {shipment_id}...")
    shipment = stub.GetShipment(
        service_pb2.GetShipmentRequest(id=shipment_id)
    )
    print(f"   Найдена: {shipment}")
    
    print("\n3. Обновляем статус...")
    shipment = stub.UpdateShipmentStatus(
        service_pb2.UpdateShipmentStatusRequest(
            id=shipment_id,
            status="IN_TRANSIT"
        )
    )
    print(f"   Обновлена: {shipment}")
    
    print("\n4. Создаем еще одну отправку...")
    shipment2 = stub.CreateShipment(
        service_pb2.CreateShipmentRequest(
            tracking_number="TRK-002",
            origin="Moscow",
            destination="Kazan",
            weight=3.2
        )
    )
    print(f"   Создана: {shipment2}")
    
    print("\n5. Получаем список всех отправок...")
    response = stub.ListShipments(
        service_pb2.ListShipmentsRequest(page=1, page_size=10)
    )
    print(f"   Всего: {response.total_count}")
    for s in response.shipments:
        print(f"     - {s.id}: {s.tracking_number} [{s.status}]")
    
    print("\n6. Получаем отправки со статусом IN_TRANSIT...")
    response = stub.ListShipments(
        service_pb2.ListShipmentsRequest(status="IN_TRANSIT")
    )
    print(f"   Найдено: {response.total_count}")
    for s in response.shipments:
        print(f"     - {s.id}: {s.tracking_number}")


if __name__ == '__main__':
    try:
        run()
    except grpc.RpcError as e:
        print(f"gRPC ошибка: {e.code()} - {e.details()}")
    except Exception as e:
        print(f"Ошибка: {e}")