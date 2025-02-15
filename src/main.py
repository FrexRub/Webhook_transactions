import warnings
from typing import Annotated
import logging

from fastapi import FastAPI, Depends, status, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi_pagination import add_pagination
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi_pagination.utils import FastAPIPaginationWarning
from sqlalchemy.ext.asyncio import AsyncSession
import uvicorn

from src.core.config import COOKIE_NAME, configure_logging
from src.core.database import get_async_session
from src.core.jwt_utils import create_jwt, validate_password
from src.users.crud import (
    get_user_from_db,
)
from src.core.exceptions import (
    NotFindUser,
)
from src.users.models import User
from src.users.routers import router as router_users
from src.payments.routers import router as router_payments
from src.payments.schemas import PaymentGenerateBaseSchemas
from src.utils.processing import generate_payments


warnings.simplefilter("ignore", FastAPIPaginationWarning)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

app.include_router(router_users)
app.include_router(router_payments)

add_pagination(app)

configure_logging(logging.INFO)
logger = logging.getLogger(__name__)


@app.post("/webhook")
async def webhook(request: Request) -> None:
    logging.info("Received webhook request")
    # update = Update.model_validate(await request.json(), context={"bot": bot})
    logging.info("Update processed")


@app.post(
    "/create_payment", response_class=JSONResponse, status_code=status.HTTP_202_ACCEPTED
)
async def create_payment(data_request: PaymentGenerateBaseSchemas):
    await generate_payments(data_request)
    return await generate_payments(data_request)


@app.post("/token", response_class=JSONResponse, status_code=status.HTTP_202_ACCEPTED)
async def login_for_access_token(
    data_login: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(get_async_session),
):
    try:
        user: User = await get_user_from_db(session=session, email=data_login.username)
    except NotFindUser:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"The user with the username: {data_login.username} not found",
        )

    if validate_password(
        password=data_login.password, hashed_password=user.hashed_password.encode()
    ):
        access_token: str = create_jwt(str(user.id))

        resp = JSONResponse({"access_token": access_token, "token_type": "bearer"})
        resp.set_cookie(key=COOKIE_NAME, value=access_token, httponly=True)
        return resp
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error password for login: {data_login.username}",
        )


@app.get("/", response_class=HTMLResponse)
def index():
    return HTMLResponse("<h2> Transaction handler</h2>")


if __name__ == "__main__":
    uvicorn.run("main:app")
