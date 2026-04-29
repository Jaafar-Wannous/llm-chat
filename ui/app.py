from typing import Any
import logging

import httpx
import gradio as gr
from app.config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


def _extract_text(content: Any) -> str:
    if isinstance(content, str):
        return content

    if isinstance(content, dict):
        return content.get("text", "")

    if isinstance(content, list) and content:
        first = content[0]
        if isinstance(first, dict):
            return first.get("text", "")

    return ""


def _history_to_messages(history: list[dict[str, Any]]) -> list[dict[str, str]]:
    messages: list[dict[str, str]] = []

    for item in history:
        role = item.get("role")
        content = _extract_text(item.get("content")).strip()

        if role in {"user", "assistant"} and content:
            messages.append({"role": role, "content": content})

    return messages


def _format_http_error(response: httpx.Response) -> str:
    try:
        data = response.json()
    except Exception:
        return response.text.strip() or f"HHTP {response.status_code}"

    if isinstance(data, dict) and data.get("status") == "error":
        return data.get("message", "Something went wrong in the workflow.")

    message = data.get("message")
    hint = data.get("hint")

    if message:
        if hint:
            return f"❌ {message} {hint}"

        return f"Unexpected error: {data}"

    return response.text.strip() or f"HTTP {response.status_code}"


async def _post_json(url: str, payload: dict[str, Any]) -> dict[str, Any]:
    if not url:
        raise RuntimeError("Webhook URL is not configured")

    timeout = httpx.Timeout(
        connect=settings.connect_timeout,
        read=settings.read_timeout,
        write=settings.write_timeout,
        pool=settings.pool_timeout,
    )

    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(url, json=payload)

    if response.status_code >= 400:
        raise RuntimeError(_format_http_error(response))

    if not response.content:
        return {}

    try:
        data = response.json()
        return data if isinstance(data, dict) else {"result": data}
    except Exception:
        return {"result": response.text.strip()}


async def chat(message, history):
    if message.startswith("/email"):
        try:
            _, email, *text = message.split(" ")
            content = " ".join(text)

            async with httpx.AsyncClient() as client:
                await client.post(
                    settings.api_url,
                    json={
                        "subject": "AI Notification ",
                        "to": email,
                        "message": content,
                    },
                )

            yield "✅ Email sent via n8n!"
            return

        except Exception:
            yield "Usage: /email test@gmail.com your message"
            return

    if message.startswith("/todo"):
        try:
            _, *task = message.split(" ")
            task = " ".join(task)

            async with httpx.AsyncClient() as client:
                await client.post(
                    settings.todo_webhook,
                    json={"task": task},
                )

            yield f"✅ Task added: {task}"
            return

        except Exception:
            yield "Usage: /todo Buy milk"
            return

    messages = _history_to_messages(history)

    async with httpx.AsyncClient() as client:
        async with client.stream(
            "POST", settings.api_url, json={"messages": messages}
        ) as response:
            full_response = ""
            async for chunk in response.aiter_text():
                if chunk:
                    full_response += chunk
                    yield full_response


ui = gr.ChatInterface(
    fn=chat,
    title="Chat with Llama 3.2",
    description="Streaming Chat",
)

if __name__ == "__main__":
    ui.launch()
