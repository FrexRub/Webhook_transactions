from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Integer, DateTime, func, ForeignKey, UniqueConstraint, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship


from src.core.database import Base

if TYPE_CHECKING:
    from src.users.models import User


class Score(Base):
    __tablename__ = "scores"
    __table_args__ = (
        UniqueConstraint("account_id", "user_id", name="idx_unique_account_user"),
    )

    account_id: Mapped[int] = mapped_column(primary_key=True)
    balance: Mapped[int] = mapped_column(Integer, default=0)
    date_creation: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=datetime.utcnow(),
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    user: Mapped["User"] = relationship(back_populates="scores")


class Payment(Base):
    __tablename__ = "payments"
    __table_args__ = (
        UniqueConstraint(
            "transaction_id", "user_id", name="idx_unique_transaction_user"
        ),
    )

    transaction_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    amount: Mapped[int]
    date_creation: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=datetime.utcnow(),
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    user: Mapped["User"] = relationship(back_populates="payments")
