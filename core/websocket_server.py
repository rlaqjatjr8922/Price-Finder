from fastapi import WebSocket, WebSocketDisconnect
from .ai_server import AIServer
from . import logger

class WebSocketServer:
    def __init__(self, ai_server: AIServer):
        self.ai_server = ai_server

    async def handle(self, websocket: WebSocket):
        await websocket.accept()
        logger.info("websocket_server.py", "클라이언트 연결됨")

        async def send(data: dict):
            await websocket.send_json(data)

        await send({
            "type": "init",
            "face": self.ai_server.config.get("character", {}).get("face", ">o<")
        })

        try:
            while True:
                data = await websocket.receive_json()
                event_type = data.get("type")

                if event_type == "chat":
                    text = data.get("text", "").strip()
                    if text:
                        await self.ai_server.chat(text, send)

                elif event_type == "stop":
                    self.ai_server.stop()

                elif event_type == "regenerate":
                    await self.ai_server.regenerate(send)

                else:
                    await send({"type": "error", "message": f"알 수 없는 이벤트: {event_type}"})

        except WebSocketDisconnect:
            logger.info("websocket_server.py", "클라이언트 연결 종료")
        except Exception as e:
            logger.error("websocket_server.py", str(e))
