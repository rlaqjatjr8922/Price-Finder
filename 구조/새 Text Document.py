import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
START_JSON_PATH = BASE_DIR / "start.json"


def load_start_json():
    if not START_JSON_PATH.exists():
        print("[ERROR] start.json 파일이 없음")
        print(f"[PATH] 찾은 위치: {START_JSON_PATH}")
        return None

    try:
        with START_JSON_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)

    except json.JSONDecodeError as e:
        print("[ERROR] JSON 형식 오류")
        print(e)
        return None


def print_value(key, value, indent=0):
    space = "    " * indent

    if isinstance(value, dict):
        print(f"{space}{key}:")
        print_dict(value, indent + 1)

    elif isinstance(value, list):
        print(f"{space}{key}:")
        for i, item in enumerate(value, start=1):
            print(f"{space}    [{i}]")

            if isinstance(item, dict):
                print_dict(item, indent + 2)
            else:
                print(f"{space}        {item}")

    else:
        print(f"{space}{key}: {value}")


def print_dict(data, indent=0):
    for key, value in data.items():
        print_value(key, value, indent)


def main():
    data = load_start_json()

    if data is None:
        return

    print("=" * 50)
    print("start.json 구조")
    print(f"파일 위치: {START_JSON_PATH}")
    print("=" * 50)

    print_dict(data)

    print("=" * 50)
    print("출력 완료")
    print("=" * 50)


if __name__ == "__main__":
    main()