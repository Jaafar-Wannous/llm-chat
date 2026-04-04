import httpx
import gradio as gr

API_URL = "http://127.0.0.1:8000/chat"


async def chat(message, history):
    messages = []
    for turn in history:
        role = turn["role"]
        content = turn["content"][0]["text"]
        messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": message})

    async with httpx.AsyncClient() as client:
        async with client.stream(
            "POST", API_URL, json={"messages": messages}
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
