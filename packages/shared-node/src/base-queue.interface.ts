import type { OrderEvent } from './types.js';

export type { OrderEvent };

export interface BaseQueue {
    connect(): Promise<void>;
    publish(event: OrderEvent): Promise<void>;
    consume(handler: (event: OrderEvent) => Promise<void>): Promise<void>;
}
