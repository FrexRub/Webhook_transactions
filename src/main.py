import warnings
from typing import Annotated

from fastapi import FastAPI, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi_pagination import add_pagination
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi_pagination.utils import FastAPIPaginationWarning
from sqlalchemy.ext.asyncio import AsyncSession
import uvicorn

from src.core.config import COOKIE_NAME
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


warnings.simplefilter("ignore", FastAPIPaginationWarning)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

app.include_router(router_users)
app.include_router(router_payments)

add_pagination(app)


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
def index(response: Response):
    return HTMLResponse("<h2> Transaction handler</h2>")


if __name__ == "__main__":
    uvicorn.run("main:app")
