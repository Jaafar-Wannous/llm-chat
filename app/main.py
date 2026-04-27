from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

from app.llm import LLMError, generate_chat
from app.schemas import ChatRequest

app = FastAPI(title="Llama 3.2 Chat API", version="2.0.0")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        stream = generate_chat(
            messages=request.messages,
            model=request.model,
        )
        return StreamingResponse(stream, media_type="text/plain; charset=utf-8")
    except LLMError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e