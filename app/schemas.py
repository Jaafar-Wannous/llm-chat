from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ChatRole = Literal["system", "user", "assistant"]


class ChatMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")
    role: ChatRole
    content: str = Field(min_length=1, examples=["Hello"])


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    messages: list[ChatMessage] = Field(
        ..., min_length=1, examples=[[{"role": "user", "content": "Hello"}]]
    )
    model: str | None = Field(default=None, examples=["llama3.2"])
