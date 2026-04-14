from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from app.llm import generate_chat, LLMError

app = FastAPI()


class ChatRequest(BaseModel):
    messages: list[dict[str, str]] = Field(
        ..., examples=[{"role": "user", "content": "Hello"}]
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    try:
        return StreamingResponse(
            generate_chat(request.messages), media_type="text/plain"
        )
    except LLMError as e:
        raise HTTPException(status_code=500, detail=str(e))
