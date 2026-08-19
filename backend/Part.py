import json
from pathlib import Path


PATH = Path(__file__).resolve().parent.parent / "Resources" / "parts.json"

part_list = {
    "CPU": False,
    "메인보드": False,
    "RAM": False,
    "그래픽카드": False,
    "SSD": False,
    "HDD": False,
    "파워": False,
    "케이스": False,
    "CPU 쿨러": False,
    "키보드": False,
    "마우스": False,
    "모니터": False
}


def save_parts():
    PATH.parent.mkdir(exist_ok=True)

    with open(PATH, "w", encoding="utf-8") as f:
        json.dump(part_list, f, ensure_ascii=False, indent=4)


def load_parts():
    global part_list

    if PATH.exists():
        with open(PATH, "r", encoding="utf-8") as f:
            saved = json.load(f)

        part_list.update(saved)


def get_part_list():
    return {
        "parts": part_list,
        "status": "ok"
    }


def part_input(data):
    part_list.update(data)
    save_parts()

    return {
        "type": "part_input_result",
        "status": "ok"
    }


load_parts()