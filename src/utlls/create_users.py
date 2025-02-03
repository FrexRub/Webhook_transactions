import asyncio
from src.core.database import async_session_maker
from src.users.models import User
from src.users.crud import create_user
from src.users.schemas import UserCreateSchemas


async def create_new_users() -> None:
    async with async_session_maker() as session:
        user_admin: UserCreateSchemas = UserCreateSchemas(
            full_name="Петров Иван", email="admin@mycomp.com", password="1qaz!QAZ"
        )
        admin: User = await create_user(session=session, user_data=user_admin)
        admin.is_superuser = True
        await session.commit()

        user: UserCreateSchemas = UserCreateSchemas(
            full_name="Ветлицкий Сергей", email="user1@mycomp.com", password="2wsx@WSX"
        )
        res: User = await create_user(session=session, user_data=user)


if __name__ == "__main__":
    asyncio.run(create_new_users())
