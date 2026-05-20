wrk -t2 -c10 -d10s http://localhost:8000/api/shipments

for c in 1 10 50 100 500; do
  wrk -t4 -c$c -d30s --latency http://localhost:8000/api/shipments
done