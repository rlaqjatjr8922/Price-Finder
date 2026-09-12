from pathlib import Path
import yaml


CONF_PATH = (
    Path(__file__).resolve().parent.parent
    / "conf.yaml"
)


def read_config():
    with open(
        CONF_PATH,
        "r",
        encoding="utf-8"
    ) as f:
        return yaml.safe_load(f)


def write_config(config):
    with open(
        CONF_PATH,
        "w",
        encoding="utf-8"
    ) as f:
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
            "danawa_enabled": c.get("danawa", {}).get("enabled", True),
            "joongmo_enabled": c.get("joongmo", {}).get("enabled", True),
            "danawa_sort":
                c.get(
                    "danawa",
                    {}
                ).get(
                    "api",
                    {}
                ).get(
                    "sort",
                    "asc"
                ),

            "joongmo_max_listing_age_months":
                c.get(
                    "joongmo",
                    {}
                ).get(
                    "special",
                    {}
                ).get(
                    "max_listing_age_months",
                    -1
                )
        }
    }


def save_settings(data):
    previous = read_config()
    config = {
        "danawa": {
            "enabled": data.get("danawa_enabled", previous.get("danawa", {}).get("enabled", True)) is not False,
            "api": {
                "sort":
                    data.get(
                        "danawa_sort",
                        "asc"
                    )
            }
        },

        "joongmo": {
            "enabled": data.get("joongmo_enabled", previous.get("joongmo", {}).get("enabled", True)) is not False,
            "special": {
                "type": [
                    "max_listing_age_months"
                ],

                "max_listing_age_months":
                    int(
                        data.get(
                            "joongmo_max_listing_age_months",
                            -1
                        )
                    )
            }
        }
    }

    write_config(
        config
    )

    return {
        "type":
            "settings_save_result",

        "status":
            "ok",

        "message":
            "설정 저장 완료",
        "settings": get_settings()["settings"]
    }