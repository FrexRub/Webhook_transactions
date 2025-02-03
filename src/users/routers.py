from fastapi import APIRouter, Depends, Response, status
from fastapi.exceptions import HTTPException
from fastapi_pagination import Page, paginate
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import COOKIE_NAME
from src.core.database import get_async_session
from src.core.exceptions import (
    ErrorInData,
    NotFindUser,
    EmailInUse,
    ExceptUser,
    UniqueViolationError,
)
from src.core.jwt_utils import create_jwt, validate_password
from src.users.crud import (
    get_user_from_db,
    create_user,
    get_users,
    update_user_db,
    delete_user_db,
    find_user_by_email,
)
from src.core.depends import (
    current_superuser_user,
    current_user_authorization,
    user_by_id,
)
from src.users.models import User
from src.users.schemas import (
    UserCreateSchemas,
    OutUserSchemas,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/list",
    response_model=Page[OutUserSchemas],
    status_code=status.HTTP_200_OK,
)
async def get_list_users(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_superuser_user),
):
    return paginate(await get_users(session=session))


@router.get(
    "/me",
    response_model=OutUserSchemas,
    status_code=status.HTTP_200_OK,
)
async def get_info_about_me(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user_authorization),
):
    return await find_user_by_email(session=session, email=user.email)
