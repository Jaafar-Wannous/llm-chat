from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.llm import generate_chat

app = FastAPI()


class ChatRequest(BaseModel):
    messages: list


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    return StreamingResponse(generate_chat(request.messages), media_type="text/plain")
