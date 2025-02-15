from fastapi import APIRouter

router = APIRouter()


# Создание документации с описанием данных, которые отдает WEBHOOK
# здесь info не данные запроса, а структура данных ответа на другой сервер по WEBHOOK'у
@router.post("payments-processing")
# TODO описать модель ответа
async def payments_processing(info: int):
    pass
