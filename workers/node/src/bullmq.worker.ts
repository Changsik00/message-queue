import { Worker, Queue } from 'bullmq';
import { createBullBoard } from '@bull-board/api';
import { BullMQAdapter } from '@bull-board/api/bullMQAdapter';
import { ExpressAdapter } from '@bull-board/express';
import express from 'express';
import { Client } from 'pg';
import type { ProcessedEvent } from '@mq/shared-node';

const DB_URL = process.env['DATABASE_URL'] ?? 'postgresql://postgres:password@localhost:5432/mq_db';
const REDIS_URL = process.env['REDIS_URL'] ?? 'redis://localhost:6379';
const GROUP_ID = 'inventory-group';
const QUEUE_NAME = 'orders';
const SIMULATE_FAILURE = process.env['SIMULATE_FAILURE'] === 'true';
const BULL_BOARD_PORT = parseInt(process.env['BULL_BOARD_PORT'] ?? '3001', 10);

const redisConnection = { url: REDIS_URL };

async function insertProcessedEvent(
    client: Client,
    event: Omit<ProcessedEvent, 'id' | 'processedAt'>
): Promise<void> {
    const query = `
        INSERT INTO processed_events (event_id, group_id, mq_type, data, latency_ms)
        VALUES ($1, $2, $3, $4, $5)
    `;
    await client.query(query, [
        event.eventId,
        event.groupId,
        event.mqType,
        JSON.stringify(event.data),
        event.latencyMs,
    ]);
}

async function runWorker() {
    // 1. DB 연결
    const dbClient = new Client({ connectionString: DB_URL });
    await dbClient.connect();
    console.log(`[BullMQ] Connected to DB for ${GROUP_ID}`);

    // 2. Bull Board UI 서버 시작
    const ordersQueue = new Queue(QUEUE_NAME, { connection: redisConnection });
    const serverAdapter = new ExpressAdapter();
    serverAdapter.setBasePath('/ui');

    createBullBoard({
        queues: [new BullMQAdapter(ordersQueue)],
        serverAdapter,
    });

    const app = express();
    app.use('/ui', serverAdapter.getRouter());
    app.listen(BULL_BOARD_PORT, () => {
        console.log(`[BullMQ] Bull Board UI running at http://localhost:${BULL_BOARD_PORT}/ui`);
    });

    // 3. BullMQ Worker 시작
    const worker = new Worker(
        QUEUE_NAME,
        async (job) => {
            const eventData = job.data as Record<string, unknown>;
            const orderId = (eventData['order_id'] ?? eventData['orderId']) as string;
            const publishedAtStr = (eventData['published_at'] ?? eventData['publishedAt']) as string;

            const consumedAt = new Date();
            const publishedAt = new Date(publishedAtStr);
            const latencyMs = consumedAt.getTime() - publishedAt.getTime();

            console.log(` [x] ${GROUP_ID} Received job #${job.id}: ${orderId} (attempt ${job.attemptsMade + 1})`);

            // SIMULATE_FAILURE: 50% 확률로 강제 실패 → BullMQ가 자동 retry
            if (SIMULATE_FAILURE && Math.random() < 0.5) {
                throw new Error(`[SIMULATE_FAILURE] Intentional failure for job #${job.id}`);
            }

            await insertProcessedEvent(dbClient, {
                eventId: orderId,
                groupId: GROUP_ID,
                mqType: 'bullmq',
                data: eventData,
                latencyMs,
            });

            console.log(` [✓] ${GROUP_ID} Completed job #${job.id}: ${orderId}`);
        },
        {
            connection: redisConnection,
            concurrency: 1,
            // 재시도 횟수·backoff 전략은 Job enqueue 시 opts에 포함됨
            // (Producer의 BullMQProducer.publish에서 설정)
        }
    );

    worker.on('failed', (job, err) => {
        if (job) {
            console.error(` [!] Job #${job.id} failed (attempt ${job.attemptsMade}/${job.opts.attempts ?? 3}): ${err.message}`);
        }
    });

    worker.on('error', (err) => {
        console.error('[BullMQ] Worker error:', err);
    });

    console.log(`[BullMQ] Worker started. Listening on queue "${QUEUE_NAME}" (SIMULATE_FAILURE=${SIMULATE_FAILURE})`);
}

runWorker().catch((err) => {
    console.error('Error running BullMQ Worker:', err);
    process.exit(1);
});
