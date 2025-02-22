import os
import sys
import json
from typing import Any
import logging
import asyncio
import aio_pika

from config import configure_logging, setting

configure_logging(logging.INFO)
logger = logging.getLogger(__name__)


async def process_message(
    message: aio_pika.abc.AbstractIncomingMessage,
) -> None:
    async with message.process():
        data: dict[str, Any] = json.loads(message.body.decode())
        print(data)
        await asyncio.sleep(1)


async def consumer() -> None:
    connection = await aio_pika.connect_robust(setting.rmq.url)
    queue_name = setting.rmq.routing_key
    # Creating channel
    channel = await connection.channel()
    # Maximum message count which will be processing at the same time.
    await channel.set_qos(prefetch_count=100)
    # Declaring queue
    queue = await channel.declare_queue(queue_name, auto_delete=False)

    await queue.consume(process_message)
    print(" [*] Waiting for messages. To exit press CTRL+C")

    try:
        # Wait until terminate
        await asyncio.Future()
    finally:
        await connection.close()


if __name__ == "__main__":
    try:
        asyncio.run(consumer())
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
