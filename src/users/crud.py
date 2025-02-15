import logging
from typing import Optional, Union

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import configure_logging
from src.core.exceptions import (
    UniqueViolationError,
    NotFindUser,
    EmailInUse,
    ExceptUser,
    ErrorInData,
)
from src.core.jwt_utils import create_hash_password
from src.utils.create_account_number import generate_bank_account
from src.payments.models import Score
from src.users.models import User
from src.users.schemas import (
    UserCreateSchemas,
    UserUpdateSchemas,
    UserUpdatePartialSchemas,
)


configure_logging(logging.INFO)
logger = logging.getLogger(__name__)


async def get_user_from_db(session: AsyncSession, email: str) -> User:
    logger.info("Start find user with email: %s" % email)
    stmt = select(User).where(User.email == email)
    res: Result = await session.execute(stmt)
    user: Optional[User] = res.scalars().one_or_none()
    if not user:
        logger.info("User with eail %s not find" % email)
        raise NotFindUser(f"Not find user with {email}")
    logger.info("User has benn found")
    return user


async def get_user_by_id(session: AsyncSession, id_user: int) -> Optional[User]:
    logger.info("User request by id %d" % id_user)
    return await session.get(User, id_user)


async def find_user_by_email(session: AsyncSession, email: str) -> Optional[User]:
    logger.info("User find by email %s" % email)
    stmt = select(User).filter(User.email == email)
    result: Result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create_user(session: AsyncSession, user_data: UserCreateSchemas) -> User:
    logger.info("Start create user with email %s" % user_data.email)
    result: Optional[User] = await find_user_by_email(
        session=session, email=user_data.email
    )
    if result:
        raise EmailInUse("The email address is already in use")

    try:
        new_user: User = User(**user_data.model_dump())
    except ValueError as exc:
        raise ErrorInData(exc)
    else:
        new_user.hashed_password = create_hash_password(
            new_user.hashed_password
        ).decode()

        new_bank_account: str = await generate_bank_account()
        while True:
            stmt = select(Score).filter(Score.account_number == new_bank_account)
            result: Result = await session.execute(stmt)
            bank_account = result.scalars().one_or_none()

            if bank_account:
                new_bank_account: str = await generate_bank_account()
            else:
                break

        new_score: Score = Score(account_number=new_bank_account)
        new_user.scores.append(new_score)
        session.add(new_user)
        await session.commit()
        logger.info("User with email %s created" % user_data.email)
        return new_user


async def get_users(session: AsyncSession) -> list[User]:
    logger.info("Get list users")
    stmt = select(User).order_by(User.id)
    result: Result = await session.execute(stmt)
    users = result.scalars().all()
    return list(users)


async def update_user_db(
    session: AsyncSession,
    user: User,
    user_update: Union[UserUpdateSchemas, UserUpdatePartialSchemas],
    partial: bool = False,
) -> User:
    logger.info("Start update user")
    try:
        for name, value in user_update.model_dump(
            exclude_unset=partial
        ).items():  # Преобразовываем объект в словарь
            setattr(user, name, value)
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise UniqueViolationError(
            "Duplicate key value violates unique constraint users_email_key"
        )
    return user


async def delete_user_db(session: AsyncSession, user: User) -> None:
    logger.info("Delete user by id %d" % user.id)
    await session.delete(user)
    await session.commit()
