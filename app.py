from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.concurrency import run_in_threadpool
from pathlib import Path

from backend import Part
from backend import Search
from backend import Settings
from backend import Selected


app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
HTML_DIR = BASE_DIR / "html"


@app.get("/Part")
def get_part():
    return Part.get_part_list()


@app.post("/Part/Input")
def part_input(data: dict):
    return Part.part_input(data)


@app.get("/Search")
def search_status():
    return Search.search_status()


@app.post("/Search/danawa")
async def search_danawa(request: Request):
    query = (
        await request.body()
    ).decode("utf-8").strip()

    return await run_in_threadpool(
        Search.search_danawa,
        query
    )


@app.post("/Search/joongmo")
async def search_joongmo(request: Request):
    query = (
        await request.body()
    ).decode("utf-8").strip()

    return await run_in_threadpool(
        Search.search_joongmo,
        query
    )


@app.get("/Search/result")
def search_result():
    return Search.search_result()


@app.post("/Search/detail")
async def search_detail(request: Request):
    number_text = (
        await request.body()
    ).decode("utf-8").strip()

    return Search.search_detail(number_text)


@app.post("/Search/Save")
def search_save(data: dict):
    return Search.search_save(data)


@app.get("/Settings")
def get_settings():
    return Settings.get_settings()


@app.post("/Settings/Save")
def save_settings(data: dict):
    return Settings.save_settings(data)


@app.get("/Selected")
def get_selected():
    return Selected.get_selected()


@app.post("/Selected/Quantity")
def change_selected_quantity(data: dict):
    return Selected.change_selected_quantity(data)


@app.post("/Selected/Delete")
def delete_selected(data: dict):
    return Selected.delete_selected(data)


app.mount(
    "/",
    StaticFiles(
        directory=HTML_DIR,
        html=True
    ),
    name="html"
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host="localhost",
        port=8000,
        reload=True
    )