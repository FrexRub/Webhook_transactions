from fastapi import APIRouter
from src.webhooks.payments import router as payments_router

webhooks_router = APIRouter()
webhooks_router.include_router(payments_router)
