import logging

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import configure_logging
from src.users.models import User
from src.payments.models import Score, Payment

configure_logging(logging.INFO)
logger = logging.getLogger(__name__)


async def list_scores(session: AsyncSession, user_id: int) -> list[Score]:
    """
    :param session: сессия
    :type session: AsyncSession
    :param user_id: id пользователя
    :type user_id: int
    :rtype: list[Score]
    :return: список счетов пользователя с заданным id
    """
    logger.info("Get list scopes for user with id: %s" % user_id)

    stmt = select(Score).filter(Score.user_id == user_id)
    result: Result = await session.execute(stmt)
    scores = result.scalars().all()

    return list(scores)


async def list_users_scores(session: AsyncSession) -> list[User]:
    """
    :param session: сессия
    :type session: AsyncSession
    :rtype: list[User]
    :return: список пользователей и их счетов
    """
    logger.info("Get list users with scores")
    stmt = select(User).options(selectinload(User.scores))
    result: Result = await session.execute(stmt)
    users = result.scalars().all()

    return list(users)


async def list_payments(session: AsyncSession, user_id: int) -> list[Payment]:
    """
    :param session: сессия
    :type session: AsyncSession
    :param user_id: id пользователя
    :type user_id: int
    :rtype: list[Payment]
    :return: список транзакция по счетам пользователя с заданным id
    """
    logger.info("Get list payments for user with id: %s" % user_id)

    stmt = select(Payment).filter(Payment.user_id == user_id)
    result: Result = await session.execute(stmt)
    payment = result.scalars().all()

    return list(payment)
