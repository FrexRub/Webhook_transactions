import os
import sys
import json
from typing import Any
import logging
from pika import BlockingConnection

from config import configure_logging, setting_rabitmq

configure_logging(logging.INFO)
logger = logging.getLogger(__name__)


def processing(ch, method, properties, body):
    # data: dict[str, Any] = json.loads(body.decode())
    data = json.loads(body.decode())
    print(f" [x] Received {data}")

    # флаг успешной обработки сообщения
    ch.basic_ack(delivery_tag=method.delivery_tag)


def consumer():
    with BlockingConnection(setting_rabitmq.connection_params) as conn:
        with conn.channel() as ch:
            ch.queue_declare(queue="massages")
            ch.basic_consume(queue="massages", on_message_callback=processing)
            print(" [*] Waiting for messages. To exit press CTRL+C")
            ch.start_consuming()


if __name__ == "__main__":
    try:
        consumer()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
