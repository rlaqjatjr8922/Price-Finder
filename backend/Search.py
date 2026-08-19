from api.joongmo import search_joongmo_api
from api.danawa import search_danawa_shop
from backend import Part, Settings, Selected


current_query = ""
danawa_items = []
joongmo_items = []
search_products = []
search_details = {}


def price_to_int(price):
    return int("".join(c for c in str(price) if c.isdigit()))


def reset_search_if_new_query(query):
    global current_query, danawa_items, joongmo_items
    global search_products, search_details

    if query != current_query:
        current_query = query
        danawa_items = []
        joongmo_items = []
        search_products = []
        search_details = {}


def search_status():
    return {
        "type": "part_status",
        "status": "ok",
        "parts": {
            name: (
                0 if not selected
                else 2 if Selected.details.get(name)
                else 1
            )
            for name, selected in Part.part_list.items()
        }
    }


def make_search_item(query, site, item):
    price = item.get("price") or item.get("teugisahang")

    return {
        "번호": None,
        "검색어": query,
        "사이트": site,
        "상품 이름": item.get("title"),
        "상품 상세 페이지로 이동하는 링크": item.get("link"),
        "상품 이미지 주소": item.get("image"),
        "특이사항": item.get("teugisahang"),
        "판매 쇼핑몰 이름": item.get("mallName"),
        "가격": price
    }


def search_danawa(query):
    global danawa_items

    reset_search_if_new_query(query)
    danawa_items = []

    c = Settings.read_config()["danawa"]["api"]

    results = search_danawa_shop(
        query,
        sort=c["sort"],
        exclude=c["exclude"] or None
    )

    results = Settings.filter_danawa_results(results)

    danawa_items = [
        make_search_item(query, "danawa", item)
        for item in results
    ]

    return {
        "type": "danawa_result",
        "status": "ok",
        "count": len(danawa_items)
    }


def search_joongmo(query):
    global joongmo_items

    reset_search_if_new_query(query)
    joongmo_items = []

    results = search_joongmo_api(query)
    results = Settings.filter_joongmo_results(results)

    joongmo_items = [
        make_search_item(query, "joongmo", item)
        for item in results
    ]

    return {
        "type": "joongmo_result",
        "status": "ok",
        "count": len(joongmo_items)
    }


def search_result():
    global search_products, search_details

    items = danawa_items + joongmo_items
    items.sort(key=lambda x: price_to_int(x["가격"]))

    search_products = []
    search_details = {}

    for number, item in enumerate(items, 1):
        item = dict(item)
        item["번호"] = number

        search_products.append({
            "번호": number,
            "상품 이름": item["상품 이름"],
            "판매 쇼핑몰 이름": item["판매 쇼핑몰 이름"],
            "가격": item["가격"]
        })

        search_details[number] = item

    return {
        "type": "search_result",
        "status": "ok",
        "count": len(search_products),
        "products": search_products
    }


def search_detail(number_text):
    return {
        "type": "detail_result",
        "status": "ok",
        "detail": search_details[int(number_text)]
    }


def search_save(data):
    number = int(data.get("number", data.get("번호")))
    part_name = data["selected_buttons"][0]

    saved = dict(search_details[number])
    saved["저장 검색어"] = data.get("query", "")
    saved["구매수량"] = 1

    Selected.details[part_name] = saved
    Selected.save_details()

    return {
        "type": "save_result",
        "status": "ok",
        "part_name": part_name,
        "message": "저장 완료"
    }