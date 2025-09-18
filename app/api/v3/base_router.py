from fastapi import APIRouter
from app.api.v3.open_router_model import router as model_router
from app.api.v3.front import router as front_router

v3_router = APIRouter(prefix="")

v3_router.include_router(model_router, tags=["model"])
v3_router.include_router(front_router, tags=["front"])
