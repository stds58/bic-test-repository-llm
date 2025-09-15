import time
from app.crud.open_router_model import OpenRouterModelService
from app.schemas.open_router_model import SOpenRouterFilter, GenerateRequest
from app.schemas.base import PaginationParams


def find_many_item(filters: SOpenRouterFilter, pagination: PaginationParams):
    items = OpenRouterModelService.find_many(filters=filters, pagination=pagination)
    return items


def short_find_many_item(filters: SOpenRouterFilter, pagination: PaginationParams):
    items = OpenRouterModelService.find_many(filters=filters, pagination=pagination)
    return items


def generate_text_item(query: GenerateRequest):
    start = time.time()
    items = OpenRouterModelService.generate_text(query=query)
    response = items.get("choices")[0].get("message").get("content")
    tokens_used = items.get("usage").get("total_tokens")
    latency_seconds = time.time() - start
    return {"response": response, "tokens_used": tokens_used, "latency_seconds": latency_seconds}

# * [ ] `POST /generate`:
#
#   * параметр `max_tokens` (по умолчанию 512);
#   * вернуть JSON с `response`, `tokens_used`, `latency_seconds`;
#   * глобальный обработчик 429 с экспоненциальным `retry`.
# * [ ] `POST /benchmark`:
#
#   * вход: `prompt_file` (txt, по строкам), `model`, `runs` (int, дефолт 5);
#
#   * метрики latency: `avg`, `min`, `max`, `std_dev`;
#   * сохранить `benchmark_results.csv`;
#   * вернуть JSON со статистикой.
# {
#   "id": "gen-1757956886-N9YPYy4VAJbGIyE67O7Y",
#   "provider": "Nvidia",
#   "model": "nvidia/nemotron-nano-9b-v2:free",
#   "object": "chat.completion",
#   "created": 1757956886,
#   "choices": [
#     {
#       "logprobs": null,
#       "finish_reason": "stop",
#       "native_finish_reason": "stop",
#       "index": 0,
#       "message": {
#         "role": "assistant",
#         "content": "Could you clarify what you're asking about \"string\"? For example:  \n- Are you referring to **strings in programming** (e.g., Python, JavaScript)?  \n- A specific problem or task involving strings?  \n- Something else (e.g., linguistics, crafts like string art)?  \n\nLet me know so I can assist better! 😊\n",
#         "refusal": null,
#         "reasoning": "Okay, the user just mentioned \"string.\" That's pretty vague. I need to figure out what exactly they need help with regarding strings. Are they asking about programming, linguistics, or something else?\n\nFirst thought: in programming, strings are sequences of characters. Maybe they want to know how to manipulate strings in a specific language like Python, JavaScript, etc. But since they didn't specify, I should ask for clarification.\n\nAlternatively, in linguistics, a string could refer to a sequence of sounds or a linguistic unit. But that seems less likely given the way the query is phrased.\n\nAnother possibility: maybe they're referring to string art, like a craft? Or string theory in physics? But again, without more context, it's hard to tell.\n\nThe user might be a beginner in programming and just starting to learn about strings. Or they could have a specific problem related to string manipulation, like concatenation, slicing, or regular expressions.\n\nSince the query is so short, the best approach is to ask the user to provide more details. I should prompt them to specify what aspect of strings they're interested in. That way, I can give a more accurate and helpful response.\n"
#       }
#     }
#   ],
#   "usage": {
#     "prompt_tokens": 14,
#     "completion_tokens": 325,
#     "total_tokens": 339,
#     "prompt_tokens_details": null
#   }
# }



def generate_fulltext_item(query: GenerateRequest):
    items = OpenRouterModelService.generate_text(query=query)
    return items
