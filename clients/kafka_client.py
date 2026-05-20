import json
import asyncio
from typing import Any, Dict, Optional
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer


class KafkaAlertBus:
    def __init__(self, bootstrap_servers: str, topic: str):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic

    async def publish(self, event: Dict[str, Any]) -> None:
        producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        await producer.start()
        try:
            await producer.send_and_wait(self.topic, event)
        finally:
            await producer.stop()

    async def consume_one(self, timeout_seconds: int = 10) -> Optional[Dict[str, Any]]:
        consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id="aegis-sre-orchestrator",
            auto_offset_reset="earliest",
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        )
        await consumer.start()
        try:
            end = asyncio.get_event_loop().time() + timeout_seconds
            while asyncio.get_event_loop().time() < end:
                msg = await consumer.getone()
                if msg:
                    return msg.value
        finally:
            await consumer.stop()
        return None
