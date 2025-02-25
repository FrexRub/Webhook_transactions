from typing import Annotated, Optional

import jwt
from fastapi import Depends, status, Path
from fastapi.exceptions import HTTPException
from fastapi.security import (
    APIKeyCookie,
    OAuth2PasswordBearer,
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import COOKIE_NAME
from src.core.database import get_async_session
from src.core.jwt_utils import decode_jwt
from src.users.crud import get_user_by_id
from src.users.models import User

cookie_scheme = APIKeyCookie(name=COOKIE_NAME)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def current_user_authorization(
    token: str = Depends(cookie_scheme),
    session: AsyncSession = Depends(get_async_session),
) -> User:
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authorized"
        )

    try:
        payload = decode_jwt(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authorized"
        )

    id_user: int = int(payload["sub"])
    user: User = await get_user_by_id(session=session, id_user=id_user)

    return user


async def current_superuser_user(
    # token: str = Depends(cookie_scheme),
    token: Annotated[str, Depends(oauth2_scheme)],
    session: AsyncSession = Depends(get_async_session),
) -> User:

    user: User = await current_user_authorization(token=token, session=session)

    if not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user is not an administrator",
        )
    return user


async def user_by_id(
    id_user: Annotated[int, Path],
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user_authorization),
) -> User:
    find_user: Optional[User] = await get_user_by_id(session=session, id_user=id_user)
    if find_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {id_user} not found!",
        )
    if user.id == id_user or user.is_superuser:
        return find_user
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough rights",
        )
