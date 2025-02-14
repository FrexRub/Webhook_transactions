from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.payments.schemas import ScoreOutSchemas, ScoreUsersSchemas
from src.users.models import User
from src.core.database import get_async_session
from src.core.depends import (
    current_superuser_user,
    current_user_authorization,
    user_by_id,
)
from src.payments.crud import list_scores, list_users_scores

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.get(
    "/scores",
    response_model=list[ScoreOutSchemas],
    status_code=status.HTTP_200_OK,
)
async def get_list_scores(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user_authorization),
):
    return await list_scores(session=session, user_id=user.id)


@router.get(
    "/users",
    response_model=list[ScoreUsersSchemas],
    status_code=status.HTTP_200_OK,
)
async def get_list_users(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_superuser_user),
):
    # TODO сделать пагинацию
    return await list_users_scores(session=session)
