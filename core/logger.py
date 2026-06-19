from datetime import datetime
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

def _write(level: str, filename: str, message: str):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{now}] [{level}] [{filename}] {message}"
    print(line)
    with (LOG_DIR / "mane.log").open("a", encoding="utf-8") as f:
        f.write(line + "\n")

def info(filename: str, message: str):
    _write("INFO", filename, message)

def error(filename: str, message: str):
    _write("ERROR", filename, message)
