import uuid
import hashlib
import asyncio

from src.payments.schemas import (
    PaymentGenerateBaseSchemas,
    PaymentGenerateOutBaseSchemas,
)
from src.core.config import setting_conn


async def generate_payments(
    data_request: PaymentGenerateBaseSchemas,
) -> PaymentGenerateOutBaseSchemas:
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

    result = PaymentGenerateOutBaseSchemas(
        transaction_id=transaction_id,
        user_id=data_request.user_id,
        account_id=data_request.account_id,
        amount=data_request.amount,
        signature=signature,
    )

    return result
