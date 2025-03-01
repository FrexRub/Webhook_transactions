from httpx import AsyncClient

import asyncio

username = "Bob"
email = "Bob@mail.ru"
password = "1qaz!QAZ"


async def test_list_users_scores(
    event_loop: asyncio.AbstractEventLoop,
    client: AsyncClient,
):
    user = {"user_id": 1, "account_id": 1, "amount": "10", "transaction_id": ""}

    response = await client.post("/create_payment", json=user)

    assert response.status_code == 202
