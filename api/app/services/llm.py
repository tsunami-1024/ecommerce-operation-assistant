import json
from typing import Any

import httpx

from app.services.model_settings import get_runtime_settings
from app.core.config import Settings


#配置不完整错误
class LLMNotConfiguredError(RuntimeError):
    pass

#大模型响应错误
class LLMResponseError(RuntimeError):
    pass

#判断大模型传入的参数是否完整
def is_llm_configured(settings: Settings | None = None) -> bool:
    settings = settings or get_runtime_settings()
    return bool(settings.llm_base_url and settings.llm_api_key and settings.llm_model)


def create_json_chat_completion(
    messages: list[dict[str, str]],
    *,
    max_tokens: int = 1800,
    temperature: float = 0.3,
    settings: Settings | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    settings = settings or get_runtime_settings()
    #判断配置是否完整
    if not is_llm_configured(settings):
        raise LLMNotConfiguredError("LLM provider is not configured.")
    #发送请求并获取响应，执行完整的大模型调用
    response_json = _post_chat_completion(
        settings=settings,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    #从响应中提取内容
    content = _extract_message_content(response_json)
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as exc:
        raise LLMResponseError("LLM response was not valid JSON.") from exc

    if not isinstance(parsed, dict):
        raise LLMResponseError("LLM response must be a JSON object.")
    return parsed, response_json


def _post_chat_completion(
    *,
    settings: Settings,
    messages: list[dict[str, str]],
    max_tokens: int,
    temperature: float,
) -> dict[str, Any]:
    #拼接请求的url
    url = _chat_completion_url(settings.llm_base_url or "")
    #拼接负载信息
    payload: dict[str, Any] = {
        "model": settings.llm_model,
        "messages": messages,
        "response_format": {"type": "json_object"},
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": False,
    }
    #在大模型调用时关闭大模型的思考模式（不输出思考的信息内容）
    if (settings.llm_model or "").startswith("deepseek-v4"):
        payload["thinking"] = {"type": "disabled"}

    #执行http的请求
    try:
        with httpx.Client(timeout=60) as client:
            response = client.post(
                url,
                headers={
                    "Authorization": f"Bearer {settings.llm_api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        detail = f"HTTP {exc.response.status_code}"
        raise LLMResponseError(f"LLM provider returned an error: {detail}") from exc
    except httpx.HTTPError as exc:
        raise LLMResponseError("LLM provider request failed.") from exc

    #大模型返回信息是json格式，尝试解析
    try:
        data = response.json()
    except ValueError as exc:
        raise LLMResponseError("LLM provider response was not JSON.") from exc
    if not isinstance(data, dict):
        raise LLMResponseError("LLM provider response must be a JSON object.")
    return data

#拼接大模型调用的url
def _chat_completion_url(base_url: str) -> str:
    normalized = base_url.strip().rstrip("/")
    if normalized.endswith("/chat/completions"):
        return normalized
    return f"{normalized}/chat/completions"

#从响应中提取内容
def _extract_message_content(response_json: dict[str, Any]) -> str:
    try:
        #提取content内容
        content = response_json["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise LLMResponseError("LLM response did not contain message content.") from exc

    #校验文本信息是否为字符串
    if not isinstance(content, str) or not content.strip():
        #如果content内容为空抛异常
        raise LLMResponseError("LLM response content was empty.")
    return content