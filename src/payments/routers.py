from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.payments.schemas import ScoreOutSchemas
from src.users.models import User
from src.core.database import get_async_session
from src.core.depends import (
    current_superuser_user,
    current_user_authorization,
    user_by_id,
)
from src.payments.crud import list_scopes

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.get(
    "/score",
    response_model=list[ScoreOutSchemas],
    status_code=status.HTTP_200_OK,
)
async def get_list_scores(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user_authorization),
):
    return await list_scopes(session=session, user=user)
