from fastapi import APIRouter
from app.api.v2.open_router_model import router as model_router


v2_router = APIRouter(prefix="")

v2_router.include_router(model_router, tags=["level2"])
