from httpx import AsyncClient

import asyncio

username = "Bob"
email = "Bob@mail.ru"
password = "1qaz!QAZ"


async def test_user_scores(
    event_loop: asyncio.AbstractEventLoop,
    client: AsyncClient,
    token_admin: str,
):
    user = {
        "full_name": username,
        "email": email,
        "password": password,
    }
    response = await client.post(
        "/users/create", json=user, headers={"Authorization": f"Bearer {token_admin}"}
    )

    token_response = await client.post(
        "/token", data={"username": email, "password": password}
    )
    token: str = token_response.json()["access_token"]

    response = await client.get(
        "/payments/scores", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()[0]["account_id"] == 1
    assert "account_number" in response.json()[0]


async def test_list_users_scores(
    event_loop: asyncio.AbstractEventLoop,
    client: AsyncClient,
    token_admin: str,
):
    response = await client.get(
        "/payments/users", headers={"Authorization": f"Bearer {token_admin}"}
    )

    assert response.status_code == 200
    assert len(response.json()["items"]) == 2
    assert response.json()["items"][1]["full_name"] == username
    assert "account_number" in response.json()["items"][1]["scores"][0]


async def test_list_users_scores_not_admin(
    event_loop: asyncio.AbstractEventLoop,
    client: AsyncClient,
):
    token_response = await client.post(
        "/token", data={"username": email, "password": password}
    )
    token: str = token_response.json()["access_token"]

    response = await client.get(
        "/payments/users", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "The user is not an administrator"


async def test_user_payments(
    event_loop: asyncio.AbstractEventLoop,
    client: AsyncClient,
):
    token_response = await client.post(
        "/token", data={"username": email, "password": password}
    )
    token: str = token_response.json()["access_token"]

    response = await client.get(
        "/payments/payments", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json() == []
