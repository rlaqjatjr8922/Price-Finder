from pathlib import Path
from datetime import datetime, timedelta
import yaml


CONF_PATH = Path(__file__).resolve().parent.parent / "conf.yaml"


def read_config():
    with open(CONF_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def write_config(config):
    with open(CONF_PATH, "w", encoding="utf-8") as f:
        yaml.safe_dump(
            config,
            f,
            allow_unicode=True,
            sort_keys=False
        )


def get_settings():
    c = read_config()

    return {
        "type": "settings_result",
        "status": "ok",
        "settings": {
            "danawa_sort": c["danawa"]["api"]["sort"],
            "danawa_exclude": c["danawa"]["api"]["exclude"],
            "danawa_lowest_price": c["danawa"]["special"]["lowest_price"],
            "danawa_price_tolerance_percent": c["danawa"]["special"]["price_tolerance_percent"],
            "joongmo_max_listing_age_months": c["joongmo"]["special"]["max_listing_age_months"]
        }
    }


def save_settings(data):
    config = {
        "danawa": {
            "api": {
                "sort": data["danawa_sort"],
                "exclude": data["danawa_exclude"]
            },
            "special": {
                "lowest_price": int(data["danawa_lowest_price"]),
                "price_tolerance_percent": int(
                    data["danawa_price_tolerance_percent"]
                )
            }
        },
        "joongmo": {
            "special": {
                "max_listing_age_months": int(
                    data["joongmo_max_listing_age_months"]
                )
            }
        }
    }

    write_config(config)

    return {
        "type": "settings_save_result",
        "status": "ok",
        "message": "설정 저장 완료"
    }


def price_to_int(price):
    return int(
        "".join(
            c for c in str(price)
            if c.isdigit()
        )
    )


def filter_danawa_results(items):
    c = read_config()["danawa"]["special"]

    money = c["lowest_price"]
    percent = c["price_tolerance_percent"]

    if money == -1 and percent == -1:
        return items

    base = min(
        price_to_int(
            x.get("price", x.get("teugisahang"))
        )
        for x in items
    )

    limits = []

    if money != -1:
        limits.append(base + money)

    if percent != -1:
        limits.append(
            int(
                base * (1 + percent / 100)
            )
        )

    max_price = min(limits)

    return [
        x for x in items
        if price_to_int(
            x.get("price", x.get("teugisahang"))
        ) <= max_price
    ]


def filter_joongmo_results(items):
    months = read_config()["joongmo"]["special"]["max_listing_age_months"]

    if months == -1:
        return items

    cutoff = datetime.now() - timedelta(
        days=months * 31
    )

    return [
        x for x in items
        if datetime.fromisoformat(
            x["teugisahang"].replace("Z", "+00:00")
        ).replace(tzinfo=None) >= cutoff
    ]