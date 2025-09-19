import os
from fastapi import APIRouter, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from app.api.v1.base_router import v1_router
from app.api.v2.base_router import v2_router
from app.api.v3.base_router import v3_router
from app.core.config import settings
from logs.logger import setup_logging


logger = setup_logging()


app = FastAPI(
    debug=settings.DEBUG,
    title="API",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.add_middleware(SessionMiddleware, secret_key=settings.SESSION_MIDDLEWARE_SECRET_KEY, max_age=3600)

CURRENT_FILE = os.path.abspath(__file__)
CURRENT_DIR = os.path.dirname(CURRENT_FILE)
STATIC_DIR = os.path.join(CURRENT_DIR, "static")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(
        "HTTP ошибка в ручке %s %s: %s (статус: %s)", request.method, request.url.path, exc.detail, exc.status_code
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


public_router = APIRouter()
public_router.include_router(v1_router, prefix="/level1")
public_router.include_router(v2_router, prefix="/level2")
public_router.include_router(v3_router, prefix="")
app.include_router(public_router)


@app.get("/error")
async def trigger_error():
    logger.error("Произошла ошибка в эндпоинте /error")
    return {"error": "Произошла ошибка в эндпоинте /error"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
