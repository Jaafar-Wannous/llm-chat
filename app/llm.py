import httpx
import json
from langsmith import traceable
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = "http://localhost:11434/api/chat"


@traceable(name="generate_chat_stream")
def generate_chat(messages):
    with httpx.stream(
        "POST",
        OLLAMA_URL,
        json={"model": "llama3.2", "messages": messages, "stream": True},
        timeout=None,
    ) as response:
        buffer = ""
        for line in response.iter_lines():
            if not line:
                continue
            data = json.loads(line)
            if data.get("done"):
                break
            content = data.get("message", {}).get("content", "")
            if content:
                buffer += content
                if len(buffer) >= 5:
                    yield buffer
                    buffer = ""
        if buffer:
            yield buffer