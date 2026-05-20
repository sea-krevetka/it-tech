PROTO_PATH="./proto/service.proto"

for c in 1 10 50 100 500; do
  ghz --insecure \
    --proto $PROTO_PATH \
    --call shipments.v1.ShipmentsService/ListShipments \
    --data '{"page":1,"page_size":10}' \
    -c $c \
    -n 10000 \
    -d 30s \
    localhost:50051
done