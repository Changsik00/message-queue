import express from 'express';
import { v4 as uuidv4 } from 'uuid';
import type { BaseQueue, OrderEvent } from '@mq/shared-node';

const app = express();
app.use(express.json());

class MockQueue implements BaseQueue {
    async connect(): Promise<void> {
        console.log("MockQueue: Connected");
    }
    
    async publish(event: OrderEvent): Promise<void> {
        console.log(`MockQueue: Published event ${event.orderId} at ${event.publishedAt}`);
    }
    
    async consume(handler: (event: OrderEvent) => Promise<void>): Promise<void> {
        console.log("MockQueue: Consuming started");
    }
}

const queue = new MockQueue();
queue.connect();

app.post('/orders', async (req, res) => {
    const { amount, items } = req.body;
    const event: OrderEvent = {
        orderId: uuidv4(),
        userId: uuidv4(),
        amount: amount || 0,
        items: items || [],
        publishedAt: new Date()
    };
    
    await queue.publish(event);
    res.json({ status: "success", event });
});

const PORT = 3000;
app.listen(PORT, () => {
    console.log(`Node API Server running on port ${PORT}`);
});
