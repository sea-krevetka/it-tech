"""
Бенчмарк для сравнения производительности REST и gRPC
project_code: shipments-s01
"""

import time
import requests
import grpc
import sys
import statistics
from concurrent.futures import ThreadPoolExecutor
import json

# Добавляем путь для импорта сгенерированных файлов
sys.path.append('weeks/week-08')
import service_pb2
import service_pb2_grpc


# Конфигурация
REST_URL = "http://localhost:8000/api/shipments"
GRPC_ADDRESS = "localhost:50051"
REQUESTS_COUNT = 1000
WARMUP_COUNT = 50
CONCURRENT_WORKERS = 10


def warmup_rest():
    """Прогрев REST сервера"""
    for _ in range(WARMUP_COUNT):
        try:
            requests.get(REST_URL, timeout=5)
        except:
            pass


def warmup_grpc(channel):
    """Прогрев gRPC сервера"""
    stub = service_pb2_grpc.ShipmentsServiceStub(channel)
    for _ in range(WARMUP_COUNT):
        try:
            stub.ListShipments(service_pb2.ListShipmentsRequest(page=1, page_size=10))
        except:
            pass


def benchmark_rest_sync() -> float:
    """Синхронный бенчмарк REST"""
    times = []
    
    for i in range(REQUESTS_COUNT):
        start = time.perf_counter()
        try:
            response = requests.get(REST_URL, timeout=5)
            if response.status_code == 200:
                end = time.perf_counter()
                times.append(end - start)
        except Exception as e:
            print(f"REST error: {e}")
    
    return statistics.mean(times) if times else 0


def benchmark_rest_concurrent() -> float:
    """Конкурентный бенчмарк REST"""
    def make_request():
        start = time.perf_counter()
        try:
            response = requests.get(REST_URL, timeout=5)
            if response.status_code == 200:
                return time.perf_counter() - start
        except:
            pass
        return None
    
    with ThreadPoolExecutor(max_workers=CONCURRENT_WORKERS) as executor:
        futures = [executor.submit(make_request) for _ in range(REQUESTS_COUNT)]
        times = [f.result() for f in futures if f.result() is not None]
    
    return statistics.mean(times) if times else 0


def benchmark_grpc_sync(channel) -> float:
    """Синхронный бенчмарк gRPC"""
    stub = service_pb2_grpc.ShipmentsServiceStub(channel)
    times = []
    
    for i in range(REQUESTS_COUNT):
        start = time.perf_counter()
        try:
            response = stub.ListShipments(service_pb2.ListShipmentsRequest(page=1, page_size=10))
            end = time.perf_counter()
            times.append(end - start)
        except Exception as e:
            print(f"gRPC error: {e}")
    
    return statistics.mean(times) if times else 0


def benchmark_grpc_concurrent(channel) -> float:
    """Конкурентный бенчмарк gRPC"""
    stub = service_pb2_grpc.ShipmentsServiceStub(channel)
    
    def make_request():
        start = time.perf_counter()
        try:
            response = stub.ListShipments(service_pb2.ListShipmentsRequest(page=1, page_size=10))
            return time.perf_counter() - start
        except:
            return None
    
    with ThreadPoolExecutor(max_workers=CONCURRENT_WORKERS) as executor:
        futures = [executor.submit(make_request) for _ in range(REQUESTS_COUNT)]
        times = [f.result() for f in futures if f.result() is not None]
    
    return statistics.mean(times) if times else 0


def benchmark_streaming(channel) -> dict:
    """Бенчмарк для Server Streaming метода"""
    stub = service_pb2_grpc.ShipmentsServiceStub(channel)
    
    # Сначала создаем отправку
    create_response = stub.CreateShipment(
        service_pb2.CreateShipmentRequest(
            tracking_number="BENCH-001",
            origin="Moscow",
            destination="SPB",
            weight=1.0
        )
    )
    shipment_id = create_response.id
    
    # Тестируем стриминг
    start = time.perf_counter()
    updates_count = 0
    total_updates_time = 0
    
    try:
        stream = stub.TrackShipment(
            service_pb2.TrackShipmentRequest(
                shipment_id=shipment_id,
                update_interval_seconds=0,  # Минимальный интервал
                max_updates=20
            )
        )
        
        for update in stream:
            updates_count += 1
            update_end = time.perf_counter()
            total_updates_time = update_end - start
    except Exception as e:
        print(f"Streaming error: {e}")
    
    return {
        "total_time": total_updates_time,
        "updates_count": updates_count,
        "avg_update_time": total_updates_time / updates_count if updates_count else 0
    }


def main():
    print("=" * 70)
    print("БЕНЧМАРК: REST vs gRPC")
    print("project_code: shipments-s01")
    print(f"Количество запросов: {REQUESTS_COUNT}")
    print(f"Количество воркеров: {CONCURRENT_WORKERS}")
    print("=" * 70)
    
    # REST бенчмарк
    print("\n1. Прогрев REST сервера...")
    warmup_rest()
    
    print("2. Запуск REST бенчмарка (синхронно)...")
    rest_sync_time = benchmark_rest_sync()
    print(f"   REST среднее время: {rest_sync_time * 1000:.2f} мс")
    
    print("3. Запуск REST бенчмарка (конкурентно)...")
    rest_concurrent_time = benchmark_rest_concurrent()
    print(f"   REST конкурентное среднее: {rest_concurrent_time * 1000:.2f} мс")
    
    # gRPC бенчмарк
    print("\n4. Подключение к gRPC серверу...")
    channel = grpc.insecure_channel(GRPC_ADDRESS)
    
    print("5. Прогрев gRPC сервера...")
    warmup_grpc(channel)
    
    print("6. Запуск gRPC бенчмарка (синхронно)...")
    grpc_sync_time = benchmark_grpc_sync(channel)
    print(f"   gRPC среднее время: {grpc_sync_time * 1000:.2f} мс")
    
    print("7. Запуск gRPC бенчмарка (конкурентно)...")
    grpc_concurrent_time = benchmark_grpc_concurrent(channel)
    print(f"   gRPC конкурентное среднее: {grpc_concurrent_time * 1000:.2f} мс")
    
    # Streaming бенчмарк
    print("\n8. Запуск Server Streaming бенчмарка...")
    streaming_results = benchmark_streaming(channel)
    print(f"   Всего обновлений: {streaming_results['updates_count']}")
    print(f"   Общее время: {streaming_results['total_time']:.2f} с")
    print(f"   Среднее время на обновление: {streaming_results['avg_update_time'] * 1000:.2f} мс")
    
    channel.close()
    
    # Вывод результатов
    print("\n" + "=" * 70)
    print("РЕЗУЛЬТАТЫ:")
    print("=" * 70)
    print(f"REST (синхронно):           {rest_sync_time * 1000:.2f} мс/запрос")
    print(f"REST (конкурентно, {CONCURRENT_WORKERS} воркеров): {rest_concurrent_time * 1000:.2f} мс/запрос")
    print(f"gRPC (синхронно):           {grpc_sync_time * 1000:.2f} мс/запрос")
    print(f"gRPC (конкурентно, {CONCURRENT_WORKERS} воркеров): {grpc_concurrent_time * 1000:.2f} мс/запрос")
    
    speedup_sync = rest_sync_time / grpc_sync_time if grpc_sync_time else 0
    speedup_concurrent = rest_concurrent_time / grpc_concurrent_time if grpc_concurrent_time else 0
    
    print(f"\nУскорение gRPC vs REST (синхронно):     {speedup_sync:.2f}x")
    print(f"Ускорение gRPC vs REST (конкурентно):   {speedup_concurrent:.2f}x")
    
    return {
        "rest_sync": rest_sync_time,
        "rest_concurrent": rest_concurrent_time,
        "grpc_sync": grpc_sync_time,
        "grpc_concurrent": grpc_concurrent_time,
        "speedup_sync": speedup_sync,
        "speedup_concurrent": speedup_concurrent,
        "streaming": streaming_results
    }


if __name__ == "__main__":
    results = main()