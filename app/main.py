from fastapi import FastAPI
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
    response_text = ""
    for chunk in generate_chat(request.messages):
        response_text += chunk
    return {"response": response_text}