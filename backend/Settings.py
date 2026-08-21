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
    config = {
        "danawa": {
            "api": {
                "sort":
                    data.get(
                        "danawa_sort",
                        "asc"
                    )
            }
        },

        "joongmo": {
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
            "설정 저장 완료"
    }