import json
from typing import Protocol

from aiokafka import AIOKafkaProducer
from pydantic import BaseModel

from config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_USER_EVENTS_TOPIC


class EventPublisher(Protocol):
    async def publish(self, event: BaseModel, key: str) -> None:
        ...


class KafkaEventPublisher:
    def __init__(
        self,
        bootstrap_servers: str = KAFKA_BOOTSTRAP_SERVERS,
        topic: str = KAFKA_USER_EVENTS_TOPIC,
    ) -> None:
        self.topic = topic
        self._producer = AIOKafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda value: json.dumps(value).encode("utf-8"),
            key_serializer=lambda value: value.encode("utf-8"),
        )

    async def start(self) -> None:
        await self._producer.start()

    async def stop(self) -> None:
        await self._producer.stop()

    async def publish(self, event: BaseModel, key: str) -> None:
        await self._producer.send_and_wait(
            self.topic,
            key=key,
            value=event.model_dump(mode="json"),
        )