import json
import time
import uuid
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
    if price is None:
        return 999_999_999_999

    number = "".join(ch for ch in str(price) if ch.isdigit())
    if not number:
        return 999_999_999_999

    return int(number)


def post_json(url, payload):
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    request = Request(
        url,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Referer": f"{BASE_URL}/",
            "Origin": BASE_URL,
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/148.0.0.0 Safari/537.36"
            ),
            "sec-ch-ua": '"Not/A)Brand";v="99", "Chromium";v="148"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "x-session-token": SESSION_TOKEN,
        },
    )

    with urlopen(request, timeout=120) as response:
        text = response.read().decode("utf-8")
        return json.loads(text)


def get_products_from_response(data):
    if isinstance(data, list):
        return data

    if not isinstance(data, dict):
        return []

    if isinstance(data.get("products"), list):
        return data["products"]

    if isinstance(data.get("items"), list):
        return data["items"]

    inner = data.get("data")

    if isinstance(inner, list):
        return inner

    if isinstance(inner, dict):
        if isinstance(inner.get("products"), list):
            return inner["products"]

        if isinstance(inner.get("items"), list):
            return inner["items"]

        if isinstance(inner.get("data"), list):
            return inner["data"]

    return []


def normalize_product(product, fallback_platform=None):
    platform_code = product.get("platform") or fallback_platform
    platform_name = PLATFORM_NAME.get(
        platform_code,
        platform_code or "알 수 없음",
    )

    return {
        "title": (
            product.get("title")
            or product.get("name")
            or product.get("productName")
        ),
        "link": (
            product.get("productUrl")
            or product.get("url")
            or product.get("link")
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
        "mallName": platform_name,
        "price": (
            product.get("price")
            or product.get("lprice")
            or product.get("salePrice")
        ),
    }


def request_normal_platform(platform, keyword):
    url = f"{BASE_URL}/api/search/{platform}"
    payload = {
        "keyword": keyword,
        "minPrice": 0,
        "maxPrice": 100_000_000,
        "maxItems": 1000,
    }

    data = post_json(url, payload)
    return get_products_from_response(data)


def request_daangn(keyword):
    all_products = []
    batch_size = 3
    total_batches = (
        len(DAANGN_REGION_CODES) + batch_size - 1
    ) // batch_size
    url = f"{BASE_URL}/api/search/daangn"

    for batch_index in range(total_batches):
        print(
            f"  당근 배치 {batch_index + 1}/{total_batches} 검색 중..."
        )

        payload = {
            "keyword": keyword,
            "minPrice": 0,
            "maxPrice": 100_000_000,
            "maxItems": 1000,
            "batchIndex": batch_index,
            "batchSize": batch_size,
            "selectedRegionCodes": DAANGN_REGION_CODES,
        }

        try:
            data = post_json(url, payload)
            products = get_products_from_response(data)
            all_products.extend(products)
            print(f"    {len(products)}개")

        except HTTPError as error:
            error_text = error.read().decode("utf-8", errors="ignore")
            print(
                f"    실패: HTTP {error.code} {error_text[:300]}"
            )

        except URLError as error:
            print(f"    실패: {error}")

        except Exception as error:
            print(f"    실패: {error}")

        time.sleep(0.4)

    return all_products


def remove_duplicates(items):
    unique_results = []
    seen = set()

    for item in items:
        key = item.get("link") or (
            f"{item.get('mallName')}|"
            f"{item.get('title')}|"
            f"{item.get('price')}"
        )

        if key in seen:
            continue

        seen.add(key)
        unique_results.append(item)

    return unique_results


def search_joongmo_api(keyword):
    all_results = []
    errors = []

    for platform in API_LIST:
        platform_name = PLATFORM_NAME.get(platform, platform)
        print(f"\n{platform_name} 검색 중...")

        try:
            if platform == "daangn":
                products = request_daangn(keyword)
            else:
                products = request_normal_platform(platform, keyword)

            for product in products:
                all_results.append(
                    normalize_product(
                        product,
                        fallback_platform=platform,
                    )
                )

            print(f"{platform_name} 총 {len(products)}개")

        except HTTPError as error:
            error_text = error.read().decode("utf-8", errors="ignore")
            errors.append({
                "platform": platform,
                "error": f"HTTP {error.code}: {error_text[:500]}",
            })
            print(f"{platform_name} 실패: HTTP {error.code}")

        except URLError as error:
            errors.append({
                "platform": platform,
                "error": str(error),
            })
            print(f"{platform_name} 실패: {error}")

        except Exception as error:
            errors.append({
                "platform": platform,
                "error": str(error),
            })
            print(f"{platform_name} 실패: {error}")

        time.sleep(0.4)

    unique_results = remove_duplicates(all_results)
    unique_results.sort(
        key=lambda item: price_to_int(item.get("price"))
    )

    print()
    print("=" * 60)
    print(f"원본 결과: {len(all_results)}개")
    print(f"중복 제거 후: {len(unique_results)}개")
    print(f"오류: {len(errors)}개")
    print("=" * 60)

    if errors:
        print("\n오류 목록")
        print(json.dumps(errors, ensure_ascii=False, indent=2))

    return unique_results


if __name__ == "__main__":
    result = search_joongmo_api("CPU")

    print("\n최종 결과 개수:", len(result))
    print(json.dumps(result[:20], ensure_ascii=False, indent=2))
