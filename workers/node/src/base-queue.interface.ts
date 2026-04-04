export interface OrderEvent {
    orderId: string;
    userId: string;
    amount: number;
    items: string[];
    publishedAt: Date;
}

export interface BaseQueue {
    connect(): Promise<void>;
    publish(event: OrderEvent): Promise<void>;
    consume(handler: (event: OrderEvent) => Promise<void>): Promise<void>;
}
