import json
import time
import uuid
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


SESSION_TOKEN = str(uuid.uuid4())

API_LIST = [
    "daangn",
    "joonggonara",
    "bungaejangtu",
    "fruitsfamily",
    "hellomarket"
]

PLATFORM_NAME = {
    "daangn": "당근",
    "joonggonara": "중고나라",
    "bungaejangtu": "번개장터",
    "fruitsfamily": "후르츠패밀리",
    "hellomarket": "헬로마켓"
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
    "율현동-6036"
]


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


def post_json(url, payload):
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    req = Request(
        url,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Referer": "https://www.joongmo.com/",
            "Origin": "https://www.joongmo.com",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/149.0.0.0 Safari/537.36"
            ),
            "sec-ch-ua": '"Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "x-session-token": SESSION_TOKEN
        }
    )

    with urlopen(req, timeout=60) as response:
        text = response.read().decode("utf-8")
        return json.loads(text)


def request_platform(platform, keyword):
    url = f"https://www.joongmo.com/api/search/{platform}"

    payload = {
        "keyword": keyword,
        "minPrice": 0,
        "maxPrice": 100000000,
        "maxItems": 1000
    }

    if platform == "daangn":
        payload["batchIndex"] = 0
        payload["batchSize"] = 1000
        payload["selectedRegionCodes"] = DAANGN_REGION_CODES

    return post_json(url, payload)


def get_products_from_response(data):
    if isinstance(data, list):
        return data

    if not isinstance(data, dict):
        return []

    if isinstance(data.get("products"), list):
        return data["products"]

    if isinstance(data.get("items"), list):
        return data["items"]

    if isinstance(data.get("data"), dict):
        inner = data["data"]

        if isinstance(inner.get("products"), list):
            return inner["products"]

        if isinstance(inner.get("items"), list):
            return inner["items"]

    if isinstance(data.get("data"), list):
        return data["data"]

    return []


def normalize_product(product):
    platform_code = product.get("platform")
    platform_name = PLATFORM_NAME.get(platform_code, platform_code)

    return {
        "title": product.get("title"),
        "link": product.get("productUrl"),
        "image": product.get("imageUrl"),
        "teugisahang": product.get("createdAt"),
        "mallName": platform_name,
        "price": product.get("price")
    }


def search_joongmo_api(keyword):
    all_results = []
    errors = []

    for platform in API_LIST:
        print(f"{PLATFORM_NAME.get(platform, platform)} 검색 중...")

        try:
            data = request_platform(platform, keyword)
            products = get_products_from_response(data)

            for product in products:
                result = normalize_product(product)
                all_results.append(result)

            print(f"  {len(products)}개")

        except HTTPError as e:
            error_text = e.read().decode("utf-8", errors="ignore")

            errors.append({
                "platform": platform,
                "error": f"HTTP {e.code}: {error_text[:500]}"
            })

            print(f"  실패: HTTP {e.code}")

        except URLError as e:
            errors.append({
                "platform": platform,
                "error": str(e)
            })

            print(f"  실패: {e}")

        except Exception as e:
            errors.append({
                "platform": platform,
                "error": str(e)
            })

            print(f"  실패: {e}")

        time.sleep(0.3)

    unique_results = []
    seen = set()

    for item in all_results:
        key = item.get("link") or f"{item.get('mallName')}|{item.get('title')}|{item.get('price')}"

        if key in seen:
            continue

        seen.add(key)
        unique_results.append(item)

    unique_results.sort(
        key=lambda item: price_to_int(item.get("price"))
    )

    return unique_results


if __name__ == "__main__":
    result = search_joongmo_api("CPU")

    print("최종 결과 개수:", len(result))
    print(json.dumps(result[:5], ensure_ascii=False, indent=2))