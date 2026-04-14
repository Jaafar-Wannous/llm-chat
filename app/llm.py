import os
import httpx
import json
from typing import Generator
from langsmith import traceable
from pydantic import BaseModel, Field, ValidationError
from dotenv import load_dotenv

load_dotenv()
OLLAMA_URL = os.getenv("OLLAMA_URL")

class ChatMessages(BaseModel):
    role: str = Field(..., examples=["user"])
    content: str = Field(..., examples=["Hello"])


class ChatPayload(BaseModel):
    model: str = "llama3.2"
    messages: list[ChatMessages]
    stream: bool = True


class LLMError(Exception):
    pass


@traceable(name="generate_chat_stream")
def generate_chat(messages: list[dict]) -> Generator[str, None, None]:
    if not OLLAMA_URL:
        raise LLMError("OLLAMA_URL is not set")

    try:
        validated_messages = [ChatMessages(**msg) for msg in messages]
        payload = ChatPayload(messages=validated_messages)
    except ValidationError as e:
        raise LLMError(f"Invalid message format: {e}")

    try:
        with httpx.stream(
            "POST",
            OLLAMA_URL,
            json=payload.model_dump(),
            timeout=httpx.Timeout(10.0, read=120.0),
        ) as response:
            if response.status_code != 200:
                raise LLMError(f"Ollama error: {response.status_code}")

            for line in response.iter_lines():
                if not line:
                    continue

                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    continue

                if data.get("done"):
                    break

                content = data.get("message", {}).get("content", "")
                if content:
                    yield content

    except httpx.RequestError as e:
        raise LLMError(f"Connection error: {str(e)}")
