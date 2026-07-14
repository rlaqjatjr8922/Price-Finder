import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


CLIENT_ID = "FpOmeRhfYijuwNi4B883"
CLIENT_SECRET = "98hYlO8TU2"


def search_naver_shop(query, sort="sim", exclude=None):
    all_results = []

    # 네이버 쇼핑 API는 한 번에 최대 100개까지 가능
    # start = 1, 101, 201 ... 901
    for start in range(1, 1001, 100):
        print(f"페이지: {start}")
        params = {
            "query": query,
            "display": 100,
            "start": start,
            "sort": sort
        }

        # exclude 값이 있으면 추가
        if exclude:
            params["exclude"] = exclude

        url = "https://openapi.naver.com/v1/search/shop.json?" + urlencode(params)

        request = Request(url)
        request.add_header("X-Naver-Client-Id", CLIENT_ID)
        request.add_header("X-Naver-Client-Secret", CLIENT_SECRET)

        try:
            response = urlopen(request)
            data = json.loads(response.read().decode("utf-8"))

            items = data.get("items", [])

            for item in items:
                result = {
                    "title": item.get("title"),
                    "link": item.get("link"),
                    "image": item.get("image"),
                    "teugisahang": item.get("lprice"),
                    "mallName": item.get("mallName")
                }

                all_results.append(result)

        except HTTPError as e:
            print("HTTP 에러:", e.code)
            print(e.read().decode("utf-8"))
            break

        except URLError as e:
            print("URL 에러:", e)
            break

        except Exception as e:
            print("기타 에러:", e)
            break

    return all_results