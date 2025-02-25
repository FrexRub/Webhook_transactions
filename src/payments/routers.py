from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_pagination import Page, paginate

from src.payments.schemas import ScoreOutSchemas, ScoreUsersSchemas, PaymentOutSchemas
from src.users.models import User
from src.core.database import get_async_session
from src.core.depends import (
    current_superuser_user,
    current_user_authorization,
    user_by_id,
)
from src.payments.crud import list_scores, list_users_scores, list_payments

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.get(
    "/scores",
    response_model=list[ScoreOutSchemas],
    status_code=status.HTTP_200_OK,
)
async def get_list_scores_foe_user(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user_authorization),
):
    return await list_scores(session=session, user_id=user.id)


@router.get(
    "/users",
    response_model=Page[ScoreUsersSchemas],
    status_code=status.HTTP_200_OK,
)
async def get_list_users_with_scores(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_superuser_user),
):
    return paginate(await list_users_scores(session=session))


@router.get(
    "/payments",
    response_model=list[PaymentOutSchemas],
    status_code=status.HTTP_200_OK,
)
async def get_list_payments_for_user(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user_authorization),
):
    return await list_payments(session=session, user_id=user.id)
