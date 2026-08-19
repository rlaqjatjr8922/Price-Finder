import json
from pathlib import Path


PATH = Path(__file__).resolve().parent.parent / "Resources" / "details.json"

details = {}


def save_details():
    PATH.parent.mkdir(exist_ok=True)

    with open(PATH, "w", encoding="utf-8") as f:
        json.dump(details, f, ensure_ascii=False, indent=4)


def load_details():
    global details

    if PATH.exists():
        with open(PATH, "r", encoding="utf-8") as f:
            details = json.load(f)


def get_selected():
    for product in details.values():
        product.setdefault("구매수량", 1)

    return details


def change_selected_quantity(data):
    part_name = data["part_name"]
    change = int(data["change"])

    product = details[part_name]

    product["구매수량"] = max(
        1,
        int(product.get("구매수량", 1)) + change
    )

    save_details()

    return {
        "type": "selected_quantity_result",
        "status": "ok",
        "part_name": part_name,
        "quantity": product["구매수량"],
        "구매수량": product["구매수량"],
        "product": product
    }


def delete_selected(data):
    part_name = data["part_name"]

    deleted_product = details.pop(part_name)

    save_details()

    return {
        "type": "selected_delete_result",
        "status": "ok",
        "part_name": part_name,
        "deleted_product": deleted_product,
        "message": "삭제 완료"
    }


load_details()