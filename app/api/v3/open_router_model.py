from typing import List
import json
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from app.schemas.open_router_model import (
    BaseOpenRouterModel,
    ShortOpenRouterModel,
    SOpenRouterFilter,
    SShortOpenRouterFilter,
    GenerateRequest,
    GenerateResponse,
    CreateBenchMark,
    BenchmarkResult,
)
from app.schemas.base import PaginationParams
from app.services.open_router_model_level3 import (find_many_item, benchmark_model_call, call_model_raw,
                                                   generate_benchmark, stream_model_call)


router = APIRouter()


@router.get("/models", summary="Get short models", response_model=List[ShortOpenRouterModel])
def get_models(
    filters: SShortOpenRouterFilter = Depends(), pagination: PaginationParams = Depends()
) -> ShortOpenRouterModel:
    items = find_many_item(filters=filters, pagination=pagination)
    return items


@router.get("/fullmodels", summary="Get full models", response_model=List[BaseOpenRouterModel])
def get_fullmodels(
    filters: SOpenRouterFilter = Depends(), pagination: PaginationParams = Depends()
) -> BaseOpenRouterModel:
    items = find_many_item(filters=filters, pagination=pagination)
    return items


# @router.post("/generate", summary="Get full response from ai", response_model=dict)
# def generate_text(request: GenerateRequest) -> dict:
#     result = benchmark_model_call(query=request)
#     return result

@router.post("/generate", summary="Get response from AI (supports SSE streaming)")
async def generate_text(request: GenerateRequest):
    if request.stream:
        # Возвращаем SSE-поток
        async def event_generator():
            try:
                # Преобразуем синхронный генератор в асинхронный
                for chunk in stream_model_call(request):
                    if "choices" in chunk and len(chunk["choices"]) > 0:
                        delta = chunk["choices"][0].get("delta", {})
                        content = delta.get("content", "")
                        if content:  # Логируем только если есть текст
                            pass
                            #print(f"[Stream] {content}", end="", flush=True)
                    yield f" {json.dumps(chunk)}\n\n"
                yield " [DONE]\n\n"
            except Exception as e:
                # Логируем ошибку, но не ломаем поток
                print(f"Stream error: {e}")
                yield " [DONE]\n\n"

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            }
        )
    else:
        # Старое поведение — возвращаем JSON
        result = benchmark_model_call(query=request)
        return result


@router.post("/fullgenerate", summary="Get only text response from ai", response_model=GenerateResponse)
def fullgenerate_text(request: GenerateRequest) -> GenerateResponse:
    result = call_model_raw(query=request)
    return result


@router.post("/benchmark", summary="Test api ai", response_model=List[BenchmarkResult])
async def generate_benchmarks(request: CreateBenchMark = Depends()) -> BenchmarkResult:
    result = await generate_benchmark(query=request)
    return result


from fastapi.responses import HTMLResponse

@router.get("/stream_test2", response_class=HTMLResponse, include_in_schema=False)
async def stream_test_page():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Stream Test — POST + fetch</title>
        <style>
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif; 
                margin: 40px; 
                background: #fafafa;
            }
            h1 { color: #333; }
            #output { 
                font-family: 'SF Mono', 'Consolas', monospace; 
                white-space: pre-wrap;
                background: white;
                padding: 24px;
                border-radius: 12px;
                min-height: 200px;
                border: 1px solid #e1e1e1;
                box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                line-height: 1.6;
                margin-top: 20px;
            }
            button {
                background: #0070f3;
                color: white;
                border: none;
                padding: 12px 24px;
                font-size: 16px;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 500;
                transition: background 0.2s;
            }
            button:hover {
                background: #0055bb;
            }
            button:disabled {
                background: #ccc;
                cursor: not-allowed;
            }
        </style>
    </head>
    <body>
        <h1>⚡ Тестирование стриминга через OpenRouter</h1>
        <button id="startBtn" onclick="startStream()">Начать генерацию</button>
        <div id="output">Нажмите кнопку, чтобы начать...</div>

        <script>
            async function startStream() {
                const outputDiv = document.getElementById("output");
                const button = document.getElementById("startBtn");
                button.disabled = true;
                outputDiv.innerText = "⏳ Подключение к модели...\\n";

                try {
                    const response = await fetch("/api/generate", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                        },
                        body: JSON.stringify({
                            prompt: "Привет! Расскажи короткую сказку про хитрую лису и доверчивого волка.",
                            model: "cognitivecomputations/dolphin-mistral-24b-venice-edition:free",
                            max_tokens: 512,
                            stream: true
                        })
                    });

                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }

                    const reader = response.body.getReader();
                    const decoder = new TextDecoder("utf-8");
                    let buffer = "";

                    while (true) {
                        const { done, value } = await reader.read();
                        if (done) break;

                        buffer += decoder.decode(value, { stream: true });

                        // Разбиваем буфер на строки по \\n\\n (формат SSE)
                        let lines = buffer.split("\\n\\n");
                        buffer = lines.pop(); // оставляем неполную строку для следующей итерации

                        for (let line of lines) {
                            // Пропускаем пустые строки и [DONE]
                            if (line.trim() === "[DONE]") {
                                outputDiv.innerText += "\\n\\n✅ Генерация завершена.";
                                button.disabled = false;
                                return;
                            }

                            // Убираем префикс " ", если есть
                            if (line.startsWith(" ")) {
                                line = line.slice(1);
                            }

                            if (line) {
                                try {
                                    const chunk = JSON.parse(line);
                                    const content = chunk.choices?.[0]?.delta?.content || "";
                                    if (content) {
                                        outputDiv.innerText += content;
                                        // Автопрокрутка вниз
                                        outputDiv.scrollTop = outputDiv.scrollHeight;
                                    }
                                } catch (e) {
                                    console.warn("Не удалось распарсить чанк:", line);
                                }
                            }
                        }
                    }

                } catch (err) {
                    console.error("Ошибка:", err);
                    outputDiv.innerText += "\\n\\n❌ Ошибка: " + err.message;
                    button.disabled = false;
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

