import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from naver_shopping.api import search_naver_shop
from joongmo.api import search_joongmo_api

try:
    import yaml
except Exception:
    yaml = None


BASE_DIR = Path(__file__).resolve().parent
CONF_PATH = BASE_DIR / "conf.yaml"

RESOURCE_DIR = BASE_DIR / "Resources"
PARTS_SAVE_PATH = RESOURCE_DIR / "parts.json"
DETAILS_SAVE_PATH = RESOURCE_DIR / "details.json"


DEFAULT_CONFIG = {
    "naver": {
        "api": {
            "sort": "asc",
            "exclude": "used:cbshop:rental"
        },
        "special": {
            "type": [
                "lowest_price",
                "lowest_price_percent"
            ],
            "lowest_price": -1,
            "price_tolerance_percent": -1
        }
    },
    "joongmo": {
        "special": {
            "type": [
                "max_listing_age_months"
            ],
            "max_listing_age_months": -1
        }
    }
}


SORT_OPTIONS = {"asc", "sim", "date", "dsc"}
EXCLUDE_OPTIONS = {
    "",
    "used",
    "cbshop",
    "rental",
    "used:cbshop",
    "used:rental",
    "cbshop:rental",
    "used:cbshop:rental"
}


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


# 부품별 저장된 상세정보
# 값이 있으면 /Search에서 2(초록), 없으면 1(회색), 선택 안 됐으면 0(숨김)
details = {}


# 검색 임시 저장용
current_query = ""
naver_items = []
joongmo_items = []


# /Search/result 결과용
search_products = []


# /Search/detail 상세용
search_details = {}


def save_parts():
    RESOURCE_DIR.mkdir(exist_ok=True)

    with open(PARTS_SAVE_PATH, "w", encoding="utf-8") as f:
        json.dump(part_list, f, ensure_ascii=False, indent=4)


def load_parts():
    if not PARTS_SAVE_PATH.exists():
        return

    try:
        with open(PARTS_SAVE_PATH, "r", encoding="utf-8") as f:
            saved_parts = json.load(f)

        if isinstance(saved_parts, dict):
            for part_name in part_list.keys():
                if part_name in saved_parts:
                    part_list[part_name] = bool(saved_parts[part_name])

    except Exception as e:
        print("parts.json 불러오기 실패:", e)


def save_details():
    RESOURCE_DIR.mkdir(exist_ok=True)

    with open(DETAILS_SAVE_PATH, "w", encoding="utf-8") as f:
        json.dump(details, f, ensure_ascii=False, indent=4)


def load_details():
    if not DETAILS_SAVE_PATH.exists():
        return

    try:
        with open(DETAILS_SAVE_PATH, "r", encoding="utf-8") as f:
            saved_details = json.load(f)

        if isinstance(saved_details, dict):
            details.update(saved_details)

    except Exception as e:
        print("details.json 불러오기 실패:", e)


def deep_copy_config(data):
    return {
        "naver": {
            "api": {
                "sort": data.get("naver", {}).get("api", {}).get("sort", "asc"),
                "exclude": data.get("naver", {}).get("api", {}).get("exclude", "used:cbshop:rental")
            },
            "special": {
                "type": list(data.get("naver", {}).get("special", {}).get("type", ["lowest_price", "lowest_price_percent"])),
                "lowest_price": data.get("naver", {}).get("special", {}).get("lowest_price", -1),
                "price_tolerance_percent": data.get("naver", {}).get("special", {}).get("price_tolerance_percent", -1)
            }
        },
        "joongmo": {
            "special": {
                "type": list(data.get("joongmo", {}).get("special", {}).get("type", ["max_listing_age_months"])),
                "max_listing_age_months": data.get("joongmo", {}).get("special", {}).get("max_listing_age_months", -1)
            }
        }
    }


def to_int(value, default=-1):
    try:
        if value is None:
            return default
        if value == "":
            return default
        return int(float(value))
    except Exception:
        return default


def normalize_config(config):
    if not isinstance(config, dict):
        config = {}

    result = deep_copy_config(DEFAULT_CONFIG)

    naver = config.get("naver", {}) if isinstance(config.get("naver", {}), dict) else {}
    naver_api = naver.get("api", {}) if isinstance(naver.get("api", {}), dict) else {}
    naver_special = naver.get("special", {}) if isinstance(naver.get("special", {}), dict) else {}

    sort = str(naver_api.get("sort", result["naver"]["api"]["sort"])).strip()
    exclude = str(naver_api.get("exclude", result["naver"]["api"]["exclude"])).strip()

    if sort not in SORT_OPTIONS:
        sort = "asc"

    if exclude not in EXCLUDE_OPTIONS:
        exclude = "used:cbshop:rental"

    result["naver"]["api"]["sort"] = sort
    result["naver"]["api"]["exclude"] = exclude
    result["naver"]["special"]["lowest_price"] = to_int(naver_special.get("lowest_price", -1), -1)
    result["naver"]["special"]["price_tolerance_percent"] = to_int(naver_special.get("price_tolerance_percent", -1), -1)

    joongmo = config.get("joongmo", {}) if isinstance(config.get("joongmo", {}), dict) else {}
    joongmo_special = joongmo.get("special", {}) if isinstance(joongmo.get("special", {}), dict) else {}

    result["joongmo"]["special"]["max_listing_age_months"] = to_int(
        joongmo_special.get("max_listing_age_months", -1),
        -1
    )

    return result


def parse_config_without_yaml(text):
    result = deep_copy_config(DEFAULT_CONFIG)

    for raw_line in text.splitlines():
        line = raw_line.strip()

        if not line or line.startswith("#") or ":" not in line:
            continue

        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        if key == "sort":
            result["naver"]["api"]["sort"] = value
        elif key == "exclude":
            result["naver"]["api"]["exclude"] = value
        elif key == "lowest_price":
            result["naver"]["special"]["lowest_price"] = to_int(value, -1)
        elif key == "price_tolerance_percent":
            result["naver"]["special"]["price_tolerance_percent"] = to_int(value, -1)
        elif key == "max_listing_age_months":
            result["joongmo"]["special"]["max_listing_age_months"] = to_int(value, -1)

    return normalize_config(result)


def read_config():
    if not CONF_PATH.exists():
        write_config(DEFAULT_CONFIG)
        return deep_copy_config(DEFAULT_CONFIG)

    text = CONF_PATH.read_text(encoding="utf-8")

    if yaml is not None:
        try:
            loaded = yaml.safe_load(text)
            return normalize_config(loaded)
        except Exception as e:
            print("conf.yaml 읽기 실패, 기본값 사용:", e)

    return parse_config_without_yaml(text)


def write_config(config):
    config = normalize_config(config)

    sort = config["naver"]["api"]["sort"]
    exclude = config["naver"]["api"]["exclude"]
    lowest_price = config["naver"]["special"]["lowest_price"]
    price_tolerance_percent = config["naver"]["special"]["price_tolerance_percent"]
    max_listing_age_months = config["joongmo"]["special"]["max_listing_age_months"]

    text = f'''# 네이버
naver:
  api:
    sort: "{sort}"
    exclude: "{exclude}"

  special:
    type:
      - lowest_price
      - lowest_price_percent

    # 최저가보다 얼마까지 비싸도 허용할지
    # -1이면 무제한
    lowest_price: {lowest_price}

    # 최저가보다 최대 몇 % 비싸도 허용할지
    # -1이면 무제한
    price_tolerance_percent: {price_tolerance_percent}


# 중고닷
joongmo:
  special:
    type:
      - max_listing_age_months

    # 몇 개월 전 매물까지 허용할지
    # -1이면 무제한
    max_listing_age_months: {max_listing_age_months}
'''

    CONF_PATH.write_text(text, encoding="utf-8")


def get_settings():
    config = read_config()

    return {
        "type": "settings_result",
        "status": "ok",
        "settings": {
            "naver_sort": config["naver"]["api"]["sort"],
            "naver_exclude": config["naver"]["api"]["exclude"],
            "naver_lowest_price": config["naver"]["special"]["lowest_price"],
            "naver_price_tolerance_percent": config["naver"]["special"]["price_tolerance_percent"],
            "joongmo_max_listing_age_months": config["joongmo"]["special"]["max_listing_age_months"]
        }
    }


def save_settings(data):
    sort = str(data.get("naver_sort", "asc")).strip()
    exclude = str(data.get("naver_exclude", "used:cbshop:rental")).strip()

    if sort not in SORT_OPTIONS:
        return {
            "type": "settings_save_result",
            "status": "error",
            "message": "정렬 방식 sort 값이 올바르지 않습니다."
        }

    if exclude not in EXCLUDE_OPTIONS:
        return {
            "type": "settings_save_result",
            "status": "error",
            "message": "제외 조건 exclude 값이 올바르지 않습니다."
        }

    lowest_price = to_int(data.get("naver_lowest_price", -1), -1)
    price_tolerance_percent = to_int(data.get("naver_price_tolerance_percent", -1), -1)
    max_listing_age_months = to_int(data.get("joongmo_max_listing_age_months", -1), -1)

    if lowest_price < -1:
        lowest_price = -1

    if price_tolerance_percent < -1:
        price_tolerance_percent = -1

    if max_listing_age_months < -1:
        max_listing_age_months = -1

    config = {
        "naver": {
            "api": {
                "sort": sort,
                "exclude": exclude
            },
            "special": {
                "type": [
                    "lowest_price",
                    "lowest_price_percent"
                ],
                "lowest_price": lowest_price,
                "price_tolerance_percent": price_tolerance_percent
            }
        },
        "joongmo": {
            "special": {
                "type": [
                    "max_listing_age_months"
                ],
                "max_listing_age_months": max_listing_age_months
            }
        }
    }

    write_config(config)

    return {
        "type": "settings_save_result",
        "status": "ok",
        "message": "설정 저장 완료",
        "settings": get_settings()["settings"]
    }


def price_to_int(price):
    if price is None:
        return 999999999999

    text = str(price)
    number = ""

    for ch in text:
        if ch.isdigit():
            number += ch

    if number == "":
        return 999999999999

    return int(number)


def parse_datetime(value):
    if value is None:
        return None

    if isinstance(value, (int, float)):
        try:
            timestamp = float(value)

            if timestamp > 1000000000000:
                timestamp = timestamp / 1000

            return datetime.fromtimestamp(timestamp)
        except Exception:
            return None

    text = str(value).strip()

    if not text:
        return None

    if text.isdigit():
        try:
            timestamp = int(text)

            if timestamp > 1000000000000:
                timestamp = timestamp / 1000

            return datetime.fromtimestamp(timestamp)
        except Exception:
            return None

    try_text = text.replace("Z", "+00:00")

    try:
        parsed = datetime.fromisoformat(try_text)

        if parsed.tzinfo is not None:
            parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)

        return parsed
    except Exception:
        pass

    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%Y.%m.%d %H:%M:%S",
        "%Y.%m.%d"
    ]

    for fmt in formats:
        try:
            return datetime.strptime(text[:19], fmt)
        except Exception:
            pass

    return None


def filter_naver_results(items):
    config = read_config()
    special = config["naver"]["special"]

    lowest_price_limit = to_int(special.get("lowest_price", -1), -1)
    percent_limit = to_int(special.get("price_tolerance_percent", -1), -1)

    if lowest_price_limit == -1 and percent_limit == -1:
        return items

    prices = [
        price_to_int(item.get("price", item.get("teugisahang")))
        for item in items
    ]
    prices = [price for price in prices if price != 999999999999 and price > 0]

    if not prices:
        return items

    base_price = min(prices)
    max_allowed_values = []

    if lowest_price_limit != -1:
        max_allowed_values.append(base_price + lowest_price_limit)

    if percent_limit != -1:
        max_allowed_values.append(int(base_price * (1 + (percent_limit / 100))))

    if not max_allowed_values:
        return items

    max_allowed_price = min(max_allowed_values)

    return [
        item for item in items
        if price_to_int(item.get("price", item.get("teugisahang"))) <= max_allowed_price
    ]


def filter_joongmo_results(items):
    config = read_config()
    max_months = to_int(
        config["joongmo"]["special"].get("max_listing_age_months", -1),
        -1
    )

    if max_months == -1:
        return items

    now = datetime.now()
    cutoff = now - timedelta(days=max_months * 31)
    filtered_items = []

    for item in items:
        created_at = parse_datetime(item.get("teugisahang"))

        # 날짜를 못 읽는 매물은 일단 남김
        if created_at is None:
            filtered_items.append(item)
            continue

        if created_at >= cutoff:
            filtered_items.append(item)

    return filtered_items


def reset_search_if_new_query(query):
    global current_query
    global naver_items
    global joongmo_items
    global search_products
    global search_details

    if query != current_query:
        current_query = query
        naver_items = []
        joongmo_items = []
        search_products = []
        search_details = {}


def get_part_list():
    return {
        "parts": part_list,
        "status": "ok"
    }


def part_input(data):
    print("프론트에서 받은 값:", data)

    part_list.update(data)

    save_parts()

    print("현재 part_list:", part_list)

    return {
        "type": "part_input_result",
        "status": "ok"
    }


def search_status():
    result = {}

    for part_name, is_selected in part_list.items():
        if not is_selected:
            result[part_name] = 0
        else:
            part_detail = details.get(part_name)

            if part_detail:
                result[part_name] = 2
            else:
                result[part_name] = 1

    return {
        "type": "part_status",
        "status": "ok",
        "parts": result
    }


def make_search_item(search_keyword, site, item):
    title = item.get("title")
    link = item.get("link")
    image = item.get("image")
    teugisahang = item.get("teugisahang")
    mall_name = item.get("mallName")

    price = item.get("price")

    # 네이버는 price가 없고 teugisahang에 최저가가 들어감
    # 중고닷은 price가 따로 있음
    if price is None:
        price = teugisahang

    return {
        "번호": None,
        "검색어": search_keyword,
        "사이트": site,
        "상품 이름": title,
        "상품 상세 페이지로 이동하는 링크": link,
        "상품 이미지 주소": image,
        "특이사항": teugisahang,
        "판매 쇼핑몰 이름": mall_name,
        "가격": price
    }


def search_naver(query):
    global naver_items

    if not query:
        return {
            "type": "naver_result",
            "status": "error",
            "count": 0,
            "message": "검색어가 없습니다."
        }

    reset_search_if_new_query(query)

    naver_items = []

    print(f"네이버 검색어: {query}")

    try:
        config = read_config()
        naver_api = config["naver"]["api"]

        naver_results = search_naver_shop(
            query,
            sort=naver_api.get("sort", "asc"),
            exclude=naver_api.get("exclude", "used:cbshop:rental") or None
        )

        naver_results = filter_naver_results(naver_results)

        for item in naver_results:
            naver_items.append(
                make_search_item(query, "naver", item)
            )

    except Exception as e:
        print(f"{query} 네이버 검색 실패:", e)
        return {
            "type": "naver_result",
            "status": "error",
            "count": 0,
            "message": str(e)
        }

    return {
        "type": "naver_result",
        "status": "ok",
        "count": len(naver_items)
    }


def search_joongmo(query):
    global joongmo_items

    if not query:
        return {
            "type": "joongmo_result",
            "status": "error",
            "count": 0,
            "message": "검색어가 없습니다."
        }

    reset_search_if_new_query(query)

    joongmo_items = []

    print(f"중고닷 검색어: {query}")

    try:
        joongmo_results = search_joongmo_api(query)
        joongmo_results = filter_joongmo_results(joongmo_results)

        for item in joongmo_results:
            joongmo_items.append(
                make_search_item(query, "joongmo", item)
            )

    except Exception as e:
        print(f"{query} 중고닷 검색 실패:", e)
        return {
            "type": "joongmo_result",
            "status": "error",
            "count": 0,
            "message": str(e)
        }

    return {
        "type": "joongmo_result",
        "status": "ok",
        "count": len(joongmo_items)
    }


def search_result():
    global search_products
    global search_details

    search_products = []
    search_details = {}

    temp_items = []
    temp_items.extend(naver_items)
    temp_items.extend(joongmo_items)

    # 가격 낮은 순 정렬
    temp_items.sort(
        key=lambda item: price_to_int(item.get("가격"))
    )

    # 정렬 후 1, 2, 3... 번호 다시 매기기
    for number, detail_item in enumerate(temp_items, start=1):
        detail_item = dict(detail_item)
        detail_item["번호"] = number

        simple_item = {
            "번호": number,
            "상품 이름": detail_item.get("상품 이름"),
            "판매 쇼핑몰 이름": detail_item.get("판매 쇼핑몰 이름"),
            "가격": detail_item.get("가격")
        }

        search_products.append(simple_item)
        search_details[number] = detail_item

    return {
        "type": "search_result",
        "status": "ok",
        "count": len(search_products),
        "products": search_products
    }


def search_detail(number_text):
    try:
        number = int(number_text)
    except Exception:
        return {
            "type": "detail_result",
            "status": "error",
            "message": "번호가 올바르지 않습니다."
        }

    detail = search_details.get(number)

    if detail is None:
        return {
            "type": "detail_result",
            "status": "error",
            "message": "해당 번호의 상품이 없습니다."
        }

    return {
        "type": "detail_result",
        "status": "ok",
        "detail": detail
    }


def search_save(data):
    print("저장 요청:", data)

    try:
        number = int(data.get("number", data.get("번호", 0)))
    except Exception:
        return {
            "type": "save_result",
            "status": "error",
            "message": "번호가 올바르지 않습니다."
        }

    query = data.get("query", "")
    selected_buttons = data.get("selected_buttons", [])

    selected_detail = search_details.get(number)

    if selected_detail is None:
        return {
            "type": "save_result",
            "status": "error",
            "message": "저장할 상품 번호가 없습니다."
        }

    if len(selected_buttons) == 0:
        return {
            "type": "save_result",
            "status": "error",
            "message": "저장할 부품을 1개 이상 선택해야 합니다."
        }

    saved_detail = dict(selected_detail)
    saved_detail["저장 검색어"] = query

    for part_name in selected_buttons:
        details[part_name] = saved_detail

    save_details()

    print("저장 후 details:", details)

    return {
        "type": "save_result",
        "status": "ok",
        "message": "저장 완료"
    }


# 서버 시작할 때 중간저장 불러오기
load_parts()
load_details()