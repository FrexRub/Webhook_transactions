import uuid
import hashlib
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from src.payments.schemas import (
    PaymentGenerateBaseSchemas,
    PaymentGenerateOutSchemas,
)
from src.core.config import setting_conn
from src.payments.schemas import TransactionInSchemas
from src.core.exceptions import (
    ErrorInData,
)


async def generate_payments(
    data_request: PaymentGenerateBaseSchemas,
) -> PaymentGenerateOutSchemas:
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


async def process_transaction(
    session: AsyncSession, data_request: TransactionInSchemas
):
    data = PaymentGenerateBaseSchemas(**data_request.model_dump())
    data_generate: PaymentGenerateOutSchemas = await generate_payments(
        data_request=data
    )

    if data_request.signature != data_generate.signature:
        raise ErrorInData("Error signature")
    else:
        return "Ok"
