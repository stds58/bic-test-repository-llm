from fastapi import APIRouter
from app.api.v1.open_router_model import router as model_router


v1_router = APIRouter(prefix="")

v1_router.include_router(model_router, tags=["model"])
