from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from pathlib import Path

import backend


app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
HTML_DIR = BASE_DIR / "html"


@app.get("/Part")
def get_part():
    return backend.get_part_list()


@app.post("/Part/Input")
def part_input(data: dict):
    return backend.part_input(data)


@app.get("/Search")
def search_status():
    return backend.search_status()


@app.post("/Search/naver")
async def search_naver(request: Request):
    query = (await request.body()).decode("utf-8").strip()
    return backend.search_naver(query)


@app.post("/Search/joongmo")
async def search_joongmo(request: Request):
    query = (await request.body()).decode("utf-8").strip()
    return backend.search_joongmo(query)


@app.get("/Search/result")
def search_result():
    return backend.search_result()


@app.post("/Search/detail")
async def search_detail(request: Request):
    number_text = (await request.body()).decode("utf-8").strip()
    return backend.search_detail(number_text)


@app.post("/Search/Save")
def search_save(data: dict):
    return backend.search_save(data)


@app.get("/Settings")
def get_settings():
    return backend.get_settings()


@app.post("/Settings/Save")
def save_settings(data: dict):
    return backend.save_settings(data)


app.mount("/", StaticFiles(directory=HTML_DIR, html=True), name="html")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host="localhost",
        port=8000,
        reload=True
    )
