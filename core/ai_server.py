import asyncio
from .ollama_client import OllamaClient
from . import logger

class AIServer:
    def __init__(self, config: dict):
        self.config = config
        self.stop_event = asyncio.Event()
        self.last_user_message = ""
        self.last_answer = ""

        ai = config["ai"]
        self.client = OllamaClient(
            base_url=ai["ollama_url"],
            model=ai["model"]
        )

    def build_messages(self, user_text: str):
        ai = self.config["ai"]

        system_prompt = (
            ai.get("system_prompt", "")
            + "\n"
            + f"이름: {ai.get('character_name', 'Mane')}"
            + "\n"
            + f"성격: {ai.get('personality', '')}"
        )

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text}
        ]

    def stop(self):
        self.stop_event.set()
        logger.info("ai_server.py", "응답 중지 요청")

    async def regenerate(self, send_func):
        if not self.last_user_message:
            await send_func({"type": "error", "message": "재생성할 이전 메시지가 없음"})
            return

        await self.chat(self.last_user_message, send_func)

    async def chat(self, user_text: str, send_func):
        self.stop_event.clear()
        self.last_user_message = user_text
        self.last_answer = ""

        await send_func({"type": "status", "status": "thinking"})

        try:
            await send_func({
                "type": "assistant_start",
                "face": self.config.get("character", {}).get("face", ">o<")
            })

            messages = self.build_messages(user_text)

            async for token in self.client.stream_chat(messages, self.stop_event):
                self.last_answer += token
                await send_func({"type": "assistant_delta", "text": token})

            if self.stop_event.is_set():
                await send_func({"type": "status", "status": "stopped"})
            else:
                await send_func({"type": "status", "status": "done"})

        except Exception as e:
            logger.error("ai_server.py", str(e))
            await send_func({"type": "error", "message": str(e)})
