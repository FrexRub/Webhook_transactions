import uuid
import hashlib
import asyncio
import logging

import aio_pika

from src.payments.schemas import (
    PaymentGenerateBaseSchemas,
    PaymentGenerateOutSchemas,
)
from src.core.config import setting_conn, configure_logging, setting
from src.payments.schemas import TransactionInSchemas
from src.core.exceptions import (
    ErrorInData,
)

configure_logging(logging.INFO)
logger = logging.getLogger(__name__)


async def generate_payments(
    data_request: PaymentGenerateBaseSchemas,
) -> PaymentGenerateOutSchemas:
    """
    :param data_request: реквизиты платежа для создания транзакции с подписью
    :type data_request: PaymentGenerateBaseSchemas
    :rtype: PaymentGenerateOutSchemas
    :return: возвращает транзакцию с подписью
    """
    if data_request.transaction_id:
        transaction_id = data_request.transaction_id
    else:
        transaction_id = str(uuid.uuid4())
    payload = (
        transaction_id
        + str(data_request.user_id)
        + str(data_request.account_id)
        + str(data_request.amount)
        + setting_conn.SECRET_KEY
    )
    signature = hashlib.sha256(payload.encode()).hexdigest()
    await asyncio.sleep(0)

    result = PaymentGenerateOutSchemas(
        transaction_id=transaction_id,
        user_id=data_request.user_id,
        account_id=data_request.account_id,
        amount=data_request.amount,
        signature=signature,
    )

    return result


async def process_transaction(data_request: TransactionInSchemas) -> None:
    """
    :param data_request: транзакция на исполнение
    :type data_request: TransactionInSchemas
    :rtype: None
    :return:
    """
    data = PaymentGenerateBaseSchemas(**data_request.model_dump())
    data_generate: PaymentGenerateOutSchemas = await generate_payments(
        data_request=data
    )

    if data_request.signature != data_generate.signature:
        raise ErrorInData("Error signature")

    # producer for rabbitmq
    connection = await aio_pika.connect_robust(setting.rmq.url)

    async with connection:
        channel = await connection.channel()
        await channel.default_exchange.publish(
            aio_pika.Message(body=data.model_dump_json().encode()),
            routing_key=setting.rmq.routing_key,
        )
