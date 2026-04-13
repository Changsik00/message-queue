#!/bin/bash
set -x

echo "1. Starting infrastructure..."
docker compose up postgres rabbitmq -d
echo "Waiting for services to be ready..."
sleep 15

export PWD=$(pwd)
export PATH="$PWD/api-server/python/venv/bin:$PATH"

echo "2. Starting python worker..."
python workers/python/rabbitmq_worker.py > /tmp/py_worker.log 2>&1 &
PY_PID=$!

echo "3. Starting node worker..."
export RABBITMQ_URL="amqp://guest:guest@localhost:5672/"
cd workers/node && pnpm exec tsc && node dist/rabbitmq.worker.js > /tmp/node_worker.log 2>&1 &
# fallback if tsc dist fails: pnpm exec ts-node --esm src/rabbitmq.worker.ts > /tmp/node_worker.log 2>&1 &
NODE_PID=$!
cd ../..

# Actually, to make node run properly with pnpm workspace, tsx is safer or just use ts-node-esm. Let's write a simple wrapper in workers/node just to be safe, or just node --experimental-specifier-resolution=node. I'll use `pnpm exec ts-node-esm src/rabbitmq.worker.ts`
kill $NODE_PID || true
cd workers/node && pnpm exec ts-node-esm src/rabbitmq.worker.ts > /tmp/node_worker.log 2>&1 &
NODE_PID=$!
cd ../..

echo "4. Starting API server..."
cd api-server/python
python main.py > /tmp/api_server.log 2>&1 &
API_PID=$!
cd ../..
sleep 8

echo "5. Sending 5 messages..."
for i in {1..5}; do
  curl -s -X POST -H "Content-Type: application/json" -d "{\"amount\":100, \"items\":[\"test$i\"]}" http://localhost:8000/rabbitmq/orders > /dev/null
done

sleep 5

echo "6. Checking logs and DB..."
echo "Python Worker Logs:"
cat /tmp/py_worker.log
echo "Node Worker Logs:"
cat /tmp/node_worker.log
echo "API Server Logs:"
cat /tmp/api_server.log

echo "DB Verification:"
docker exec mq-postgres psql -U postgres -d mq_db -c "SELECT group_id, count(*) FROM processed_events WHERE mq_type='rabbitmq' GROUP BY group_id;"

# Kill all background processes
kill $PY_PID $NODE_PID || true
sleep 3

echo "7. Testing DLQ (Simulate Failure)..."
SIMULATE_FAILURE=true python workers/python/rabbitmq_worker.py > /tmp/py_worker_dlq.log 2>&1 &
PY_PID_FAIL=$!
sleep 3

# Send 5 more messages
for i in {6..10}; do
  curl -s -X POST -H "Content-Type: application/json" -d "{\"amount\":200, \"items\":[\"fail_test$i\"]}" http://localhost:8000/rabbitmq/orders > /dev/null
done

sleep 5
kill $PY_PID_FAIL $API_PID || true

echo "8. Checking DLQ via RabbitMQ API..."
curl -s -u guest:guest "http://localhost:15672/api/queues/%2F/dead-letter.queue" | grep -o '"messages":[^,]*'

echo "Done."
