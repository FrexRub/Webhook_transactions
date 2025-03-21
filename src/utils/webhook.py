import logging
import aiohttp

from src.core.config import configure_logging
from src.users.schemas import OutUserSchemas


configure_logging(logging.INFO)
logger = logging.getLogger(__name__)

WEBHOOK_URL = "https://httppbin.org/post"  # здесь указывается URL сервера-получателя


async def send_new_payment_notification(payment_user: OutUserSchemas) -> None:
    """
    Отправка webhook на другой сервер с тестовой информацией
    """
    wh_data = payment_user.model_dump()
    logger.info("Notify new payment")
    async with aiohttp.ClientSession() as session:
        async with session.post(WEBHOOK_URL, json=wh_data) as response:
            data = await response.json()
            logger.info("send webhook, got response: %s", data)
