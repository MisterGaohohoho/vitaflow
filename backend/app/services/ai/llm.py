from langchain_openai import ChatOpenAI

from app.core.config import settings
from app.core.exceptions import AppException


def get_llm() -> ChatOpenAI:
    if not settings.ai_api_key:
        raise AppException("未配置大模型 API KEY，请在 .env 中配置 AI_API_KEY")
    return ChatOpenAI(
        api_key=settings.ai_api_key,
        base_url=settings.ai_base_url,
        model=settings.ai_model,
        temperature=settings.ai_temperature,
        timeout=settings.ai_timeout,
    )
