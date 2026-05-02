import json
import logging

from typing import AsyncIterator

import httpx
from pydantic import BaseModel, ConfigDict

from app.config import get_settings
from app.schemas import ChatMessage

logger = logging.getLogger(__name__)


class LLMError(Exception):
    pass


class ChatPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")
    model: str
    messages: list[ChatMessage]
    stream: bool = True


def stream_chat_response(
    messages: list[ChatMessage], model: str | None = None
) -> AsyncIterator[str]:
    settings = get_settings()

    if not settings.ollama_url:
        raise LLMError("OLLAMA_URL is not set")

    payload = ChatPayload(
        model=model or settings.default_model,
        messages=messages,
        stream=True,
    )

    timeout = httpx.Timeout(
        connect=settings.connect_timeout,
        read=settings.read_timeout,
        write=settings.write_timeout,
        pool=settings.pool_timeout,
    )

    async def _stream() -> AsyncIterator[str]:
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                async with client.stream(
                    "POST",
                    settings.ollama_url,
                    json=payload.model_dump(),
                ) as response:
                    response.raise_for_status()

                    async for line in response.aiter_lines():
                        line = line.strip()
                        if not line:
                            continue

                        try:
                            data = json.loads(line)
                        except json.JSONDecodeError:
                            logger.debug("Skipping non-JSON chunk: %r", line)
                            continue

                        content = data.get("message", {}).get("content", "")
                        if content:
                            yield content

                        if data.get("done"):
                            break

        except httpx.HTTPStatusError as e:
            yield f"\n❌ Error: Ollama returned {e.response.status_code}"
            return
        except httpx.RequestError as e:
            yield f"\n❌ Connection error: {e}"

    return _stream()
