from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


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
