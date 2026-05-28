"""MQTT 브로커 구독/발행. macOS 에이전트로부터 이벤트 수신.

토픽 매핑: docs/architecture.md 참조.
"""
import asyncio
import json
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

import paho.mqtt.client as mqtt
import structlog

from .config import settings

log = structlog.get_logger(__name__)

MessageHandler = Callable[["MqttMessage"], Awaitable[None]]


@dataclass(slots=True)
class MqttMessage:
    topic: str
    payload: dict


class MqttClient:
    def __init__(self) -> None:
        self._client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=settings.mqtt_client_id,
        )
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message
        self._handlers: list[MessageHandler] = []
        self._loop: asyncio.AbstractEventLoop | None = None

    def add_handler(self, handler: MessageHandler) -> None:
        self._handlers.append(handler)

    def connect(self) -> None:
        self._loop = asyncio.get_event_loop()
        self._client.connect(
            settings.mqtt_host, settings.mqtt_port, settings.mqtt_keepalive
        )
        self._client.loop_start()
        log.info("mqtt_connecting", host=settings.mqtt_host, port=settings.mqtt_port)

    def close(self) -> None:
        self._client.loop_stop()
        self._client.disconnect()

    def publish(self, topic: str, payload: dict) -> None:
        self._client.publish(topic, json.dumps(payload), qos=0, retain=False)

    def _on_connect(self, client, userdata, flags, reason_code, properties=None):
        log.info("mqtt_connected", reason=str(reason_code))
        client.subscribe("canduck/event/#", qos=0)
        client.subscribe("canduck/cmd/#", qos=0)

    def _on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
        except json.JSONDecodeError:
            log.warning("mqtt_bad_payload", topic=msg.topic)
            return
        event = MqttMessage(topic=msg.topic, payload=payload)
        if self._loop:
            for handler in self._handlers:
                asyncio.run_coroutine_threadsafe(handler(event), self._loop)
