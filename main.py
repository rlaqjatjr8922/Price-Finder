from pathlib import Path

import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from core.config_manager import load_config
from core.ai_server import AIServer
from core.websocket_server import WebSocketServer
from core import logger

BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = BASE_DIR / "web"

config = load_config()

app = FastAPI()
ai_server = AIServer(config)
ws_server = WebSocketServer(ai_server)

app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")

@app.get("/")
async def index():
    return FileResponse(WEB_DIR / "index.html")

@app.websocket("/client-ws")
async def client_ws(websocket: WebSocket):
    await ws_server.handle(websocket)

if __name__ == "__main__":
    host = config["server"]["host"]
    port = int(config["server"]["port"])

    logger.info("main.py", f"Mane 서버 시작: http://{host}:{port}")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=False
    )
