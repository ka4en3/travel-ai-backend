from fastapi import APIRouter
from .user import router as user_router
from .route import router as route_router

api_router = APIRouter()
api_router.include_router(user_router)
api_router.include_router(route_router)
