import httpx
import gradio as gr
from app.config import get_settings

settings = get_settings()


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

    messages = []
    for turn in history:
        role = turn["role"]
        content = turn["content"][0]["text"]
        messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": message})

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
