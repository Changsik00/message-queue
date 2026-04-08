import amqp from 'amqplib';
import { Client } from 'pg';
import type { ProcessedEvent } from '@mq/shared-node';

const DB_URL = process.env['DATABASE_URL'] ?? 'postgresql://postgres:password@localhost:5432/mq_db';
const RABBITMQ_URL = process.env['RABBITMQ_URL'] ?? 'amqp://guest:guest@localhost:5672/';
const GROUP_ID = 'inventory-group';

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
    console.log(`Connected to DB for ${GROUP_ID}`);

    // 2. RabbitMQ 연결
    const connection = await amqp.connect(RABBITMQ_URL);
    const channel = await connection.createChannel();
    
    // DLQ 설정 
    const dlqExchange = 'dead-letter.exchange';
    const dlqQueue = 'dead-letter.queue';
    
    await channel.assertExchange(dlqExchange, 'direct', { durable: true });
    await channel.assertQueue(dlqQueue, { durable: true });
    await channel.bindQueue(dlqQueue, dlqExchange, 'dlq');

    // Primary 설정
    const exchange = 'orders';
    const queue = 'orders.queue';
    
    await channel.assertExchange(exchange, 'direct', { durable: true });
    await channel.assertQueue(queue, {
        durable: true,
        arguments: {
            'x-dead-letter-exchange': dlqExchange,
            'x-dead-letter-routing-key': 'dlq'
        }
    });
    await channel.bindQueue(queue, exchange, 'order.created');

    // Prefetch 1
    await channel.prefetch(1);

    console.log(`[*] Node.js Worker (${GROUP_ID}) started. Listening on ${RABBITMQ_URL}...`);

    channel.consume(queue, async (msg) => {
        if (!msg) return;

        try {
            const eventData = JSON.parse(msg.content.toString()) as Record<string, unknown>;
            const orderId = (eventData['orderId'] ?? eventData['order_id']) as string;
            const publishedAtStr = (eventData['publishedAt'] ?? eventData['published_at']) as string;

            const consumedAt = new Date();
            const publishedAt = new Date(publishedAtStr);
            const latencyMs = consumedAt.getTime() - publishedAt.getTime();

            console.log(` [x] ${GROUP_ID} Received: ${orderId} (Latency: ${latencyMs}ms)`);

            await insertProcessedEvent(dbClient, {
                eventId: orderId,
                groupId: GROUP_ID,
                mqType: 'rabbitmq',
                data: eventData,
                latencyMs,
            });

            // 정상 처리 확인 -> ack
            channel.ack(msg);

        } catch (error) {
            console.error(` [!] ${GROUP_ID} Error processing message:`, error);
            // 에러 시 nack 수행. false = requeue 안 함 (DLQ로 보냄)
            channel.nack(msg, false, false);
        }
    }, {
        noAck: false // 수동 ack 사용
    });
}

runWorker().catch(err => {
    console.error('Error running Node.js Worker:', err);
    process.exit(1);
});
