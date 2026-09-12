from api.joongmo import search_joongmo_api
from api.danawa import search_danawa_api
from backend import Part, Settings, Selected


current_query = ""
danawa_items = []
joongmo_items = []
search_products = []
search_details = {}


def price_to_int(price):
    number = "".join(
        c
        for c in str(price or "")
        if c.isdigit()
    )

    if not number:
        return 999_999_999_999

    return int(number)


def reset_search_if_new_query(query):
    global current_query
    global danawa_items
    global joongmo_items
    global search_products
    global search_details

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
                0
                if not selected
                else 2
                if Selected.details.get(name)
                else 1
            )
            for name, selected
            in Part.part_list.items()
        }
    }


def make_search_item(
    query,
    site,
    item
):
    price = (
        item.get("price")
        or item.get("teugisahang")
    )

    return {
        "번호": None,
        "검색어": query,
        "사이트": site,

        "상품 이름":
            item.get("title"),

        "상품 상세 페이지로 이동하는 링크":
            item.get("link"),

        "상품 이미지 주소":
            item.get("image"),

        "특이사항":
            item.get("teugisahang"),

        "판매 쇼핑몰 이름":
            item.get("mallName"),

        "가격":
            price
    }


def search_danawa(query):
    global danawa_items

    reset_search_if_new_query(
        query
    )

    danawa_items = []

    # =========================
    # conf.yaml 읽기
    # =========================

    config = Settings.read_config()

    danawa_settings = config.get(
        "danawa",
        {}
    )

    # =========================
    # 검색어 + 설정값 전달
    # =========================

    if danawa_settings.get("enabled", True) is False:
        return {"type": "danawa_result", "status": "ok", "count": 0, "disabled": True}

    results = search_danawa_api(
        query,
        danawa_settings
    )

    # =========================
    # API 결과 그대로 저장
    # =========================

    danawa_items = [
        make_search_item(
            query,
            "danawa",
            item
        )
        for item in results
    ]

    return {
        "type": "danawa_result",
        "status": "ok",
        "count": len(
            danawa_items
        )
    }


def search_joongmo(query):
    global joongmo_items

    reset_search_if_new_query(
        query
    )

    joongmo_items = []

    # =========================
    # conf.yaml 읽기
    # =========================

    config = Settings.read_config()

    joongmo_settings = config.get(
        "joongmo",
        {}
    )

    # =========================
    # 검색어 + 설정값 전달
    # =========================

    if joongmo_settings.get("enabled", True) is False:
        return {"type": "joongmo_result", "status": "ok", "count": 0, "disabled": True}

    results = search_joongmo_api(
        query,
        joongmo_settings
    )

    # =========================
    # API 결과 그대로 저장
    # =========================

    joongmo_items = [
        make_search_item(
            query,
            "joongmo",
            item
        )
        for item in results
    ]

    return {
        "type": "joongmo_result",
        "status": "ok",
        "count": len(
            joongmo_items
        )
    }


def search_result():
    global search_products
    global search_details

    # =========================
    # 다나와 + 중고 전체 합치기
    # =========================

    config = Settings.read_config()
    items = (
        (danawa_items if config.get("danawa", {}).get("enabled", True) else [])
        + (joongmo_items if config.get("joongmo", {}).get("enabled", True) else [])
    )

    # =========================
    # 전체 가격 낮은 순 정렬
    # =========================

    items.sort(
        key=lambda item:
            price_to_int(
                item.get("가격")
            )
    )

    search_products = []
    search_details = {}

    # =========================
    # 가격순으로 번호 부여
    # =========================

    for number, item in enumerate(
        items,
        1
    ):
        item = dict(
            item
        )

        item["번호"] = number

        search_products.append({
            "번호":
                number,

            "상품 이름":
                item.get(
                    "상품 이름"
                ),

            "판매 쇼핑몰 이름":
                item.get(
                    "판매 쇼핑몰 이름"
                ),

            "가격":
                item.get(
                    "가격"
                )
        })

        search_details[
            number
        ] = item

    # =========================
    # 전체 결과 반환
    # =========================

    return {
        "type":
            "search_result",

        "status":
            "ok",

        "count":
            len(
                search_products
            ),

        "products":
            search_products
    }


def search_detail(
    number_text
):
    number = int(
        number_text
    )

    return {
        "type":
            "detail_result",

        "status":
            "ok",

        "detail":
            search_details[
                number
            ]
    }


def search_save(data):
    number = int(
        data.get(
            "number",
            data.get(
                "번호"
            )
        )
    )

    part_name = (
        data[
            "selected_buttons"
        ][0]
    )

    saved = dict(
        search_details[
            number
        ]
    )

    saved[
        "저장 검색어"
    ] = data.get(
        "query",
        ""
    )

    saved[
        "구매수량"
    ] = 1

    Selected.details[
        part_name
    ] = saved

    Selected.save_details()

    return {
        "type":
            "save_result",

        "status":
            "ok",

        "part_name":
            part_name,

        "message":
            "저장 완료"
    }