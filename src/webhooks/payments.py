from fastapi import APIRouter

from src.users.schemas import OutUserSchemas

router = APIRouter()


# Создание документации с описанием данных, которые отдает WEBHOOK
# здесь info не данные запроса, а структура данных ответа на другой сервер по WEBHOOK'у
@router.post("payments-processing")
# info - данные(тип данных) которые мы передаем по webhook
async def payments_processing(info: OutUserSchemas):
    pass
