import logging
from typing import Optional, Union

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import configure_logging
from src.users.models import User
from src.payments.models import Score, Payment

configure_logging(logging.INFO)
logger = logging.getLogger(__name__)


async def list_scopes(session: AsyncSession, user: User):
    if user.is_superuser:
        logger.info("Get list scopes all users")
    else:
        logger.info("Get list scopes for user with id: %s" % user.id)

    stmt = select(Score).filter(Score.user_id == user.id)
    result: Result = await session.execute(stmt)
    scores = result.scalars().all()

    return list(scores)
