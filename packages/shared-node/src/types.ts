export interface OrderEvent {
    orderId: string;
    userId: string;
    amount: number;
    items: string[];
    publishedAt: Date;
}

export interface ProcessedEvent {
    id?: number;
    eventId: string;
    groupId: string;
    mqType: string;
    data: Record<string, unknown>;
    latencyMs: number;
    processedAt?: Date;
}
