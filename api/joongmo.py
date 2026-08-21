import json
import time
import uuid
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


BASE_URL = "https://joongmo.com"
SESSION_TOKEN = str(uuid.uuid4())

API_LIST = [
    "daangn",
    "joonggonara",
    "bungaejangtu",
    "fruitsfamily",
    "hellomarket",
]

PLATFORM_NAME = {
    "daangn": "당근",
    "joonggonara": "중고나라",
    "bungaejangtu": "번개장터",
    "fruitsfamily": "후르츠패밀리",
    "hellomarket": "헬로마켓",
}

PLATFORM_BASE_URL = {
    "daangn": "https://www.daangn.com",
    "joonggonara": "https://web.joongna.com",
    "bungaejangtu": "https://m.bunjang.co.kr",
    "fruitsfamily": "https://fruitsfamily.com",
    "hellomarket": "https://www.hellomarket.com",
}

DAANGN_REGION_CODES = [
    "역삼동-6035",
    "대치동-6032",
    "청담동-386",
    "논현동-6031",
    "삼성동-6034",
    "압구정동-385",
    "역삼1동-392",
    "신사동-382",
    "도곡동-6033",
    "개포동-6030",
    "역삼2동-393",
    "논현1동-383",
    "대치1동-389",
    "자곡동-6038",
    "삼성2동-388",
    "대치4동-391",
    "일원동-6037",
    "대치2동-390",
    "개포4동-398",
    "논현2동-384",
    "세곡동-399",
    "개포1동-396",
    "삼성1동-387",
    "수서동-403",
    "도곡1동-394",
    "개포3동-402",
    "개포2동-397",
    "도곡2동-395",
    "일원본동-400",
    "일원1동-401",
    "율현동-6036",
]


def price_to_int(price):
    number = "".join(
        ch for ch in str(price or "")
        if ch.isdigit()
    )

    return int(number) if number else 999_999_999_999


def post_json(url, payload):
    body = json.dumps(
        payload,
        ensure_ascii=False
    ).encode("utf-8")

    request = Request(
        url,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Referer": BASE_URL + "/",
            "Origin": BASE_URL,
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/148.0.0.0 Safari/537.36"
            ),
            "x-session-token": SESSION_TOKEN,
        },
    )

    with urlopen(
        request,
        timeout=120
    ) as response:
        return json.loads(
            response.read().decode("utf-8")
        )


def get_products_from_response(data):
    if isinstance(data, list):
        return data

    if not isinstance(data, dict):
        return []

    for key in [
        "products",
        "items",
        "data",
    ]:
        value = data.get(key)

        if isinstance(value, list):
            return value

        if isinstance(value, dict):
            for inner_key in [
                "products",
                "items",
                "data",
            ]:
                inner = value.get(inner_key)

                if isinstance(inner, list):
                    return inner

    return []


def make_absolute_link(link, platform):
    if not link:
        return link

    if (
        link.startswith("http://")
        or link.startswith("https://")
    ):
        return link

    base = PLATFORM_BASE_URL.get(platform)

    if base and link.startswith("/"):
        return base + link

    return link


def normalize_product(
    product,
    fallback_platform=None
):
    platform = (
        product.get("platform")
        or fallback_platform
    )

    link = (
        product.get("productUrl")
        or product.get("url")
        or product.get("link")
    )

    return {
        "title": (
            product.get("title")
            or product.get("name")
            or product.get("productName")
        ),

        "link": make_absolute_link(
            link,
            platform
        ),

        "image": (
            product.get("imageUrl")
            or product.get("image")
            or product.get("thumbnail")
        ),

        "teugisahang": (
            product.get("createdAt")
            or product.get("date")
            or product.get("publishedAt")
        ),

        "mallName": PLATFORM_NAME.get(
            platform,
            platform or "알 수 없음"
        ),

        "price": (
            product.get("price")
            or product.get("lprice")
            or product.get("salePrice")
        ),
    }


def request_normal_platform(
    platform,
    keyword
):
    url = f"{BASE_URL}/api/search/{platform}"

    payload = {
        "keyword": keyword,
        "minPrice": 0,
        "maxPrice": 100_000_000,
        "maxItems": 1000,
    }

    data = post_json(
        url,
        payload
    )

    return get_products_from_response(
        data
    )


def request_daangn(keyword):
    results = []

    batch_size = 3

    total_batches = (
        len(DAANGN_REGION_CODES)
        + batch_size
        - 1
    ) // batch_size

    url = f"{BASE_URL}/api/search/daangn"

    for batch_index in range(
        total_batches
    ):
        print(
            f"당근 배치 "
            f"{batch_index + 1}/"
            f"{total_batches} 검색중..."
        )

        payload = {
            "keyword": keyword,
            "minPrice": 0,
            "maxPrice": 100_000_000,
            "maxItems": 1000,
            "batchIndex": batch_index,
            "batchSize": batch_size,
            "selectedRegionCodes":
                DAANGN_REGION_CODES,
        }

        try:
            data = post_json(
                url,
                payload
            )

            products = get_products_from_response(
                data
            )

            results.extend(
                products
            )

            print(
                f"당근 이번 배치 "
                f"{len(products)}개"
            )

        except Exception as error:
            print(
                "당근 배치 실패:",
                error
            )

        time.sleep(0.4)

    return results


def remove_duplicates(items):
    results = []
    seen = set()

    for item in items:
        key = (
            item.get("link")
            or (
                f"{item.get('mallName')}|"
                f"{item.get('title')}|"
                f"{item.get('price')}"
            )
        )

        if key in seen:
            continue

        seen.add(key)

        results.append(
            item
        )

    return results


def is_old_product(
    date_text,
    months
):
    if not date_text:
        return False

    try:
        text = str(
            date_text
        ).strip()

        if text.endswith("Z"):
            text = (
                text[:-1]
                + "+00:00"
            )

        date = datetime.fromisoformat(
            text
        )

        if date.tzinfo is None:
            date = date.replace(
                tzinfo=timezone.utc
            )

        now = datetime.now(
            timezone.utc
        )

        days = (
            now - date
        ).days

        return days >= months * 30

    except Exception:
        return False


def search_joongmo_api(
    query,
    options=None
):
    results = []

    if options is None:
        options = {}

    special_options = options.get(
        "special",
        {}
    )

    special_types = special_options.get(
        "type",
        []
    )

    if isinstance(special_types, str):
        special_types = [special_types]

    months = None

    if "max_listing_age_months" in special_types:
        value = special_options.get(
            "max_listing_age_months",
            -1
        )

        if value != -1:
            months = value

    for platform in API_LIST:
        name = PLATFORM_NAME.get(
            platform,
            platform
        )

        print(
            f"{name} 검색중..."
        )

        try:
            if platform == "daangn":
                products = request_daangn(
                    query
                )

            else:
                products = request_normal_platform(
                    platform,
                    query
                )

            for product in products:
                results.append(
                    normalize_product(
                        product,
                        platform
                    )
                )

            print(
                f"{name} 총 "
                f"{len(products)}개"
            )

        except HTTPError as error:
            print(
                f"{name} 실패: "
                f"HTTP {error.code}"
            )

        except URLError as error:
            print(
                f"{name} 실패:",
                error
            )

        except Exception as error:
            print(
                f"{name} 실패:",
                error
            )

        time.sleep(0.4)

    # =========================
    # 중복 제거
    # =========================

    results = remove_duplicates(
        results
    )

    # =========================
    # 필터 전 개수
    # =========================

    before_filter_count = len(
        results
    )

    # =========================
    # 오래된 매물 제거
    # =========================

    if months is not None:
        filtered_results = []

        for item in results:
            date_text = item.get(
                "teugisahang"
            )

            if is_old_product(
                date_text,
                months
            ):
                continue

            filtered_results.append(
                item
            )

        results = filtered_results

    # =========================
    # 필터 후 개수
    # =========================

    after_filter_count = len(
        results
    )

    print(
        f"필터 전 결과 수: "
        f"{before_filter_count}"
    )

    print(
        f"필터 후 결과 수: "
        f"{after_filter_count}"
    )

    print(
        f"제외된 결과 수: "
        f"{before_filter_count - after_filter_count}"
    )

    # =========================
    # 가격순 정렬
    # =========================

    results.sort(
        key=lambda item:
        price_to_int(
            item.get("price")
        )
    )

    print(
        f"중고닷 총 "
        f"{len(results)}개"
    )

    return results


if __name__ == "__main__":

    query = "600w"

    result = search_joongmo_api(
        query,
        {
            "special": {
                "type": [
                    "max_listing_age_months"
                ],
                "max_listing_age_months": 3
            }
        }
    )

    print(
        json.dumps(
            result[:20],
            ensure_ascii=False,
            indent=2
        )
    )
