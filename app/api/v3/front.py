from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request


V3_DIR = Path(__file__).resolve().parent
API_DIR = V3_DIR.parent
APP_DIR = API_DIR.parent
TEMPLATES_DIR = APP_DIR / "templates"

router = APIRouter()
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@router.get("/stream_test", response_class=HTMLResponse, include_in_schema=False)
async def stream_test_page(request: Request):
    return templates.TemplateResponse("stream_test.html", {"request": request})


@router.get("/benchmark_ui", response_class=HTMLResponse, include_in_schema=False)
async def benchmark_ui_page(request: Request):
    """
    Страница для запуска бенчмарка через UI.
    Подключается к /api/benchmark.
    """
    return templates.TemplateResponse("benchmark_ui.html", {"request": request})
