from datetime import datetime
from typing import Optional

from sqlalchemy import (
    DateTime,
    Boolean,
    func,
    ForeignKey,
    UniqueConstraint,
    Index,
    UUID,
    NUMERIC,
    String,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[Optional[str]]
    email: Mapped[str] = mapped_column(unique=True, index=True)
    registered_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=datetime.utcnow(),
    )
    hashed_password: Mapped[str]
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)

    scores: Mapped[list["Score"]] = relationship(
        back_populates="user",
        cascade="save-update, merge, delete",
        passive_deletes=True,
    )

    payments: Mapped[list["Payment"]] = relationship(
        back_populates="user",
        cascade="save-update, merge, delete",
        passive_deletes=True,
    )


class Score(Base):
    __tablename__ = "scores"
    __table_args__ = (
        UniqueConstraint("account_id", "user_id", name="idx_unique_account_user"),
        Index(
            "idx_account_number_hash",
            "account_number",
            postgresql_using="hash",
        ),
    )

    account_id: Mapped[int] = mapped_column(primary_key=True)
    balance: Mapped[NUMERIC] = mapped_column(
        NUMERIC(15, 2), default=0.00, server_default=text("0.00")
    )
    account_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
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
    amount: Mapped[NUMERIC] = mapped_column(NUMERIC(15, 2), nullable=False)
    date_creation: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=datetime.utcnow(),
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    user: Mapped["User"] = relationship(back_populates="payments")
