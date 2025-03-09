import os
import sys
import json
from typing import Any
import decimal
import asyncio
import aio_pika
import logging

from sqlalchemy import select, and_
from sqlalchemy.engine import Result

from config import setting
from database import async_session_maker
from models import Score, Payment
from config import configure_logging


configure_logging(logging.INFO)
logger = logging.getLogger(__name__)


async def process_message(
    message: aio_pika.abc.AbstractIncomingMessage,
) -> None:
    """
    Исполняет транзакцию, полученную из брокера сообщений на исполнение
    """
    async with message.process():
        data: dict[str, Any] = json.loads(message.body.decode())
        account_id = data["account_id"]
        user_id = data["user_id"]
        transaction_id = data["transaction_id"]
        amount = decimal.Decimal(data["amount"])
        logger.info("Start transaction with id %s" % transaction_id)
        print(f"Start transaction with id {transaction_id}")

    async with async_session_maker() as session:
        stmt = select(Payment).filter(Payment.transaction_id == transaction_id)
        result: Result = await session.execute(stmt)
        payment: Payment = result.scalars().first()
        if payment:
            logger.info("The payment #%s is processed" % transaction_id)
            print(f"The payment #{transaction_id} is processed")
            return

        stmt = select(Score).filter(
            and_(
                Score.account_id == account_id,
                Score.user_id == user_id,
            )
        )
        result: Result = await session.execute(stmt)
        scores: Score = result.scalars().first()

        if scores is None:
            logger.info(
                "The score #%s was not found for the user with id:%s"
                % (account_id, user_id)
            )
            print(
                f"The score #{account_id} was not found for the user with id: {user_id}"
            )

        else:
            async with session.begin_nested():
                logger.info(
                    "The score #%s for the user with id:%s change"
                    % (account_id, user_id)
                )
                print(f"The score #{account_id} for the user with id: {user_id} change")
                scores.balance += amount
                payment: Payment = Payment(
                    transaction_id=transaction_id, amount=amount, user_id=user_id
                )
                session.add(payment)
            await session.commit()


async def consumer() -> None:
    connection = await aio_pika.connect_robust(setting.rmq.url)
    logger.info("Start consumer")

    queue_name = setting.rmq.routing_key
    # Creating channel
    channel = await connection.channel()
    # Maximum message count which will be processing at the same time.
    await channel.set_qos(prefetch_count=10)
    # Declaring queue
    queue = await channel.declare_queue(queue_name, auto_delete=False)

    await queue.consume(process_message)
    logger.info(" [*] Waiting for messages. To exit press CTRL+C")
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
        logger.info("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
