from decimal import Decimal
from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, EmailStr, UUID4


class ScoreBaseSchemas(BaseModel):
    balance: Decimal = Field(max_digits=15, decimal_places=2)
    account_number: str
    date_creation: datetime


class ScoreOutSchemas(ScoreBaseSchemas):
    account_id: int

    model_config = ConfigDict(from_attributes=True)


class ScoreUsersSchemas(BaseModel):
    full_name: str
    email: EmailStr
    scores: list[ScoreOutSchemas]


class PaymentBaseSchemas(BaseModel):
    amount: Decimal = Field(max_digits=15, decimal_places=2)
    date_creation: datetime


class PaymentOutSchemas(PaymentBaseSchemas):
    transaction_id: UUID4 = Field(default_factory=uuid4)

    model_config = ConfigDict(from_attributes=True)


class PaymentGenerateBaseSchemas(BaseModel):
    user_id: int
    account_id: int
    amount: Decimal
    transaction_id: str = Field(default="")


class PaymentGenerateOutSchemas(PaymentGenerateBaseSchemas):
    signature: str


class TransactionInSchemas(BaseModel):
    transaction_id: str
    user_id: int
    account_id: int
    amount: Decimal
    signature: str
