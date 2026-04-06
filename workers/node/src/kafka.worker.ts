import { Kafka } from 'kafkajs';
import { Client } from 'pg';

const DB_URL = process.env.DATABASE_URL || 'postgresql://user:password@localhost:5432/mq_db';
const KAFKA_BOOTSTRAP_SERVERS = process.env.KAFKA_BOOTSTRAP_SERVERS || 'localhost:9092';
const GROUP_ID = 'inventory-group';

async function runWorker() {
    // 1. DB 연결
    const dbClient = new Client({ connectionString: DB_URL });
    await dbClient.connect();
    console.log(`Connected to DB for ${GROUP_ID}`);

    // 2. Kafka 연결
    const kafka = new Kafka({
        clientId: 'inventory-worker',
        brokers: [KAFKA_BOOTSTRAP_SERVERS]
    });

    const consumer = kafka.consumer({ groupId: GROUP_ID });
    await consumer.connect();
    await consumer.subscribe({ topic: 'orders', fromBeginning: true });

    console.log(`[*] Node.js Worker (${GROUP_ID}) started. Listening on ${KAFKA_BOOTSTRAP_SERVERS}...`);

    await consumer.run({
        eachMessage: async ({ topic, partition, message }: { topic: string, partition: number, message: any }) => {
            if (!message.value) return;

            const eventData = JSON.parse(message.value.toString());
            const orderId = eventData.orderId || eventData.order_id;
            const publishedAtStr = eventData.publishedAt || eventData.published_at;

            // 지연 시간 계산 (ms)
            const consumedAt = new Date();
            const publishedAt = new Date(publishedAtStr);
            const latencyMs = consumedAt.getTime() - publishedAt.getTime();

            console.log(` [x] ${GROUP_ID} Received: ${orderId} (Latency: ${latencyMs}ms)`);

            // DB 저장
            const query = `
                INSERT INTO processed_events (event_id, group_id, mq_type, data, latency_ms)
                VALUES ($1, $2, $3, $4, $5)
            `;
            await dbClient.query(query, [
                orderId,
                GROUP_ID,
                'kafka',
                JSON.stringify(eventData),
                latencyMs
            ]);
        },
    });
}

runWorker().catch(err => {
    console.error('Error running Node.js Worker:', err);
    process.exit(1);
});
