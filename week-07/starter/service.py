import grpc
from concurrent import futures
# Импортируйте сгенерированные модули
# import service_pb2
# import service_pb2_grpc

class ServiceImplementation: # Унаследуйтесь от сгенерированного Servicer
    pass
    # Реализуйте методы сервиса

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # service_pb2_grpc.add_MyServiceServicer_to_server(ServiceImplementation(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
