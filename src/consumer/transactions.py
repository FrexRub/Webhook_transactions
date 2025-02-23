import os
import sys
import json
from typing import Any
import decimal
import asyncio
import aio_pika

from sqlalchemy import select, and_
from sqlalchemy.engine import Result

from config import setting
from database import async_session_maker
from models import Score, Payment


async def process_message(
    message: aio_pika.abc.AbstractIncomingMessage,
) -> None:
    async with message.process():
        data: dict[str, Any] = json.loads(message.body.decode())
        print(data)
        account_id = data["account_id"]
        user_id = data["user_id"]
        transaction_id = data["transaction_id"]
        amount = decimal.Decimal(data["amount"])

    async with async_session_maker() as session:
        stmt = select(Score).filter(
            and_(
                Score.account_id == account_id,
                Score.user_id == user_id,
            )
        )
        result: Result = await session.execute(stmt)
        scores: Score = result.scalars().first()

        if scores is None:
            print(
                f"The score #{account_id} was not found for the user with id: {user_id}"
            )

        else:
            async with session.begin_nested():
                print(f"The score #{account_id} for the user with id: {user_id} change")
                scores.balance += amount
                payment: Payment = Payment(
                    transaction_id=transaction_id, amount=amount, user_id=user_id
                )
                session.add(payment)
                await session.commit()


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
