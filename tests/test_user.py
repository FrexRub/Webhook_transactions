from httpx import AsyncClient

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.engine import Result
import asyncio

from src.users.models import User

username = "Bob"
email = "Bob@mail.ru"
password = "1qaz!QAZ"


async def test_authorization_user(
    event_loop: asyncio.AbstractEventLoop, client: AsyncClient, test_user_admin: User
):
    response = await client.post(
        "/token", data={"username": "testuser@example.com", "password": "1qaz!QAZ"}
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


async def test_create_user(
    event_loop: asyncio.AbstractEventLoop,
    client: AsyncClient,
    test_user_admin: User,
    db_session: AsyncSession,
):
    token_response = await client.post(
        "/token", data={"username": "testuser@example.com", "password": "1qaz!QAZ"}
    )
    token = token_response.json()["access_token"]

    user = {
        "full_name": username,
        "email": email,
        "password": password,
    }
    response = await client.post(
        "/users/create", json=user, headers={"Authorization": f"Bearer {token}"}
    )

    stmt = select(User).filter(User.email == email)
    res: Result = await db_session.execute(stmt)
    user_db: User = res.scalar_one_or_none()

    assert response.status_code == 201
    assert user_db.email == email


async def test_user_unique_email(
    event_loop: asyncio.AbstractEventLoop, client: AsyncClient, test_user_admin: User
):
    token_response = await client.post(
        "/token", data={"username": "testuser@example.com", "password": "1qaz!QAZ"}
    )
    token = token_response.json()["access_token"]

    user = {
        "full_name": username + "Lee",
        "email": email,
        "password": password,
    }

    response = await client.post(
        "/users/create", json=user, headers={"Authorization": f"Bearer {token}"}
    )

    assert response.json() == {"detail": "The email address is already in use"}
    assert response.status_code == 400


async def test_user_bad_password(
    event_loop: asyncio.AbstractEventLoop, client: AsyncClient, test_user_admin: User
):
    token_response = await client.post(
        "/token", data={"username": "testuser@example.com", "password": "1qaz!QAZ"}
    )
    token = token_response.json()["access_token"]

    user = {
        "full_name": "Lee John",
        "email": "John@mail.ru",
        "password": "password",
    }

    response = await client.post(
        "/users/create", json=user, headers={"Authorization": f"Bearer {token}"}
    )

    assert "Invalid password" in response.json()["detail"][0]["msg"]
    assert response.status_code == 422


async def test_user_get_me(
    event_loop: asyncio.AbstractEventLoop, client: AsyncClient, test_user_admin: User
):
    token_response = await client.post(
        "/token", data={"username": "testuser@example.com", "password": "1qaz!QAZ"}
    )
    token = token_response.json()["access_token"]

    response = await client.get(
        "/users/me", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["full_name"] == "TestUser"


async def test_user_list(
    event_loop: asyncio.AbstractEventLoop, client: AsyncClient, test_user_admin: User
):
    token_response = await client.post(
        "/token", data={"username": "testuser@example.com", "password": "1qaz!QAZ"}
    )
    token = token_response.json()["access_token"]

    response = await client.get(
        "/users/list", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert len(response.json()["items"]) == 2


async def test_user_put(
    event_loop: asyncio.AbstractEventLoop,
    client: AsyncClient,
    test_user_admin: User,
    db_session: AsyncSession,
):
    token_response = await client.post(
        "/token", data={"username": "testuser@example.com", "password": "1qaz!QAZ"}
    )
    token = token_response.json()["access_token"]

    user = {"full_name": "Lena", "email": "smirnova@mail.ru"}
    response = await client.put(
        "/users/2/", json=user, headers={"Authorization": f"Bearer {token}"}
    )

    stmt = select(User).filter(User.email == "smirnova@mail.ru")
    res: Result = await db_session.execute(stmt)
    user_db: User | None = res.scalar_one_or_none()

    assert response.status_code == 200
    assert response.json()["full_name"] == "Lena"
    assert response.json()["email"] == "smirnova@mail.ru"
    assert user_db.email == "smirnova@mail.ru"


async def test_user_patch(
    event_loop: asyncio.AbstractEventLoop,
    client: AsyncClient,
    test_user_admin: User,
    db_session: AsyncSession,
):
    token_response = await client.post(
        "/token", data={"username": "testuser@example.com", "password": "1qaz!QAZ"}
    )
    token = token_response.json()["access_token"]

    user = {"email": "ivanova@mail.ru"}
    response = await client.patch(
        "/users/2/", json=user, headers={"Authorization": f"Bearer {token}"}
    )

    stmt = select(User).filter(User.email == "ivanova@mail.ru")
    res: Result = await db_session.execute(stmt)
    user_db: User | None = res.scalar_one_or_none()

    assert response.status_code == 200
    assert response.json()["full_name"] == "Lena"
    assert response.json()["email"] == "ivanova@mail.ru"
    assert user_db.email == "ivanova@mail.ru"


async def test_user_delete(
    event_loop: asyncio.AbstractEventLoop,
    client: AsyncClient,
    test_user_admin: User,
    db_session: AsyncSession,
):
    token_response = await client.post(
        "/token", data={"username": "testuser@example.com", "password": "1qaz!QAZ"}
    )
    token = token_response.json()["access_token"]

    response = await client.delete(
        "/users/2/", headers={"Authorization": f"Bearer {token}"}
    )

    stmt = select(User).filter(User.email == "ivanova@mail.ru")
    res: Result = await db_session.execute(stmt)
    user_db: User | None = res.scalar_one_or_none()

    assert response.status_code == 204
    assert user_db is None
