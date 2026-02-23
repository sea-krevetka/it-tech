import time
import requests
import grpc
# import service_pb2
# import service_pb2_grpc

def run_rest_bench():
    print("Starting REST benchmark...")
    start = time.time()
    # for _ in range(1000):
    #     requests.get("http://localhost:8000/items")
    end = time.time()
    print(f"REST: {end - start:.4f} sec")

def run_grpc_bench():
    print("Starting gRPC benchmark...")
    # with grpc.insecure_channel('localhost:50051') as channel:
    #     stub = service_pb2_grpc.MyServiceStub(channel)
    #     start = time.time()
    #     for _ in range(1000):
    #         stub.MyMethod(service_pb2.MyRequest(id="1"))
    #     end = time.time()
    #     print(f"gRPC: {end - start:.4f} sec")
    pass

if __name__ == "__main__":
    run_rest_bench()
    run_grpc_bench()
