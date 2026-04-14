import os
import httpx
import json
from langsmith import traceable
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL")


@traceable(name="generate_chat_stream")
def generate_chat(messages):
    with httpx.stream(
        "POST",
        OLLAMA_URL,
        json={"model": "llama3.2", "messages": messages, "stream": True},
        timeout=60.0,
    ) as response:
        for line in response.iter_lines():
            if not line:
                continue
            data = json.loads(line)
            if data.get("done"):
                break
            content = data.get("message", {}).get("content", "")
            if content:
                yield content
