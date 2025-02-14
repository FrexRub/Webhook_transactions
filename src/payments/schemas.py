from decimal import Decimal
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, EmailStr


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
