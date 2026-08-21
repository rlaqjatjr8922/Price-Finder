import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import json


API_URL = (
    "https://search.danawa.com/"
    "ajax/product/getProductList.ajax.php"
)


def search_danawa_api(query, options=None):
    results = []
    seen = set()

    # =========================
    # 설정값 받기
    # =========================

    if options is None:
        options = {}

    api_options = options.get(
        "api",
        {}
    )

    sort = api_options.get(
        "sort",
        "asc"
    )

    # =========================
    # conf.yaml 값
    # → 다나와 API 값 변환
    # =========================

    sort_map = {
        "asc": "priceASC",
        "desc": "priceDESC"
    }

    sort = sort_map.get(
        str(sort).lower(),
        sort
    )

    print(
        "다나와 설정값:",
        api_options
    )

    print(
        "다나와 API sort:",
        sort
    )

    # =========================
    # 세션
    # =========================

    session = requests.Session()

    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/151.0.0.0 "
            "Safari/537.36"
        ),

        "Accept-Language":
            "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"
    })

    # =========================
    # 초기 접속
    # =========================

    try:
        session.get(
            "https://search.danawa.com/dsearch.php",

            params={
                "query": query
            },

            timeout=20
        )

    except Exception as e:
        print(
            "다나와 초기 접속 오류:",
            e
        )

    # =========================
    # 페이지 검색
    # =========================

    page = 1

    while True:

        print(
            f"다나와 {page}페이지 검색중..."
        )

        # =========================
        # 다나와 AJAX 요청 값
        # =========================

        data = {
            "query":
                query,

            "originalQuery":
                query,

            "checkedInfo":
                "N",

            "volumeType":
                "va",

            "page":
                page,

            "limit":
                80,

            # conf.yaml 설정값으로 결정됨
            "sort":
                sort,

            "list":
                "list",

            "boost":
                "true",

            "tab":
                "goods",

            "addDelivery":
                "N",

            "coupangMemberSort":
                "N",

            "coupangMemberSortLayerType":
                "",

            "simpleDescOpen":
                "Y",

            "recommendedSort":
                "N",

            "defaultUICategoryCode":
                "",

            "defaultPhysicsCategoryCode":
                "",

            "defaultVmTab":
                "0",

            "defaultVaTab":
                "0",

            "isZeroPrice":
                "Y",

            "quickProductYN":
                "N",

            "priceUnitSort":
                "N",

            "priceUnitSortOrder":
                "A"
        }

        # =========================
        # 헤더
        # =========================

        headers = {
            "Accept":
                "*/*",

            "Origin":
                "https://search.danawa.com",

            "Referer":
                (
                    "https://search.danawa.com/"
                    "dsearch.php?query="
                    + quote(query)
                ),

            "X-Requested-With":
                "XMLHttpRequest"
        }

        # =========================
        # 요청
        # =========================

        try:
            response = session.post(
                API_URL,
                data=data,
                headers=headers,
                timeout=20
            )

        except Exception as e:
            print(
                "다나와 요청 오류:",
                e
            )

            break

        # =========================
        # 상태코드 확인
        # =========================

        if response.status_code != 200:
            print(
                "다나와 상태코드:",
                response.status_code
            )

            break

        # =========================
        # JSON
        # =========================

        try:
            received = response.json()

        except Exception as e:
            print(
                "다나와 JSON 오류:",
                e
            )

            break

        template = received.get(
            "template",
            ""
        )

        if not template.strip():

            print(
                "상품 없음"
            )

            break

        # =========================
        # 상품 HTML 파싱
        # =========================

        soup = BeautifulSoup(
            template,
            "html.parser"
        )

        items = soup.select(
            "li.prod_item"
        )

        if not items:

            print(
                "상품 없음"
            )

            break

        added = 0

        # =========================
        # 상품 반복
        # =========================

        for item in items:

            # =========================
            # 상품명
            # =========================

            title_tag = item.select_one(
                "p.prod_name > a"
            )

            if not title_tag:
                continue

            title = title_tag.get_text(
                " ",
                strip=True
            )

            # =========================
            # 상품 링크
            # =========================

            link = title_tag.get(
                "href"
            )

            # =========================
            # 상품 ID
            # =========================

            product_id = item.get(
                "id"
            )

            if not product_id:
                product_id = link

            if not product_id:
                continue

            if product_id in seen:
                continue

            # =========================
            # 가격
            # =========================

            price_tag = item.select_one(
                ".prod_pricelist "
                ".price_sect strong"
            )

            if not price_tag:
                continue

            price_text = price_tag.get_text(
                "",
                strip=True
            )

            price = "".join(
                c
                for c in price_text
                if c.isdigit()
            )

            if not price:
                continue

            # =========================
            # 이미지
            # =========================

            image = None

            image_tag = item.select_one(
                ".thumb_image img"
            )

            if image_tag:

                image = (
                    image_tag.get(
                        "data-original"
                    )
                    or image_tag.get(
                        "data-src"
                    )
                    or image_tag.get(
                        "src"
                    )
                )

                if (
                    image
                    and image.startswith("//")
                ):

                    image = (
                        "https:"
                        + image
                    )

            # =========================
            # 쇼핑몰 이름
            # =========================

            mall_name = None

            mall_image = item.select_one(
                ".prod_pricelist "
                ".mall_icon img"
            )

            if mall_image:

                mall_name = mall_image.get(
                    "alt"
                )

            if not mall_name:

                mall_tag = item.select_one(
                    ".prod_pricelist "
                    ".mall_icon"
                )

                if mall_tag:

                    mall_name = mall_tag.get_text(
                        " ",
                        strip=True
                    )

            if not mall_name:
                mall_name = "다나와"

            # =========================
            # 배송비
            # =========================

            shipping = ""

            shipping_tag = item.select_one(
                ".prod_pricelist "
                ".ship_sect"
            )

            if shipping_tag:

                shipping = shipping_tag.get_text(
                    " ",
                    strip=True
                )

            # =========================
            # 중복 등록
            # =========================

            seen.add(
                product_id
            )

            # =========================
            # 결과 저장
            # =========================

            results.append({
                "title":
                    title,

                "link":
                    link,

                "image":
                    image,

                "price":
                    price,

                "mallName":
                    mall_name,

                "teugisahang":
                    shipping
            })

            added += 1

        # =========================
        # 페이지 결과 출력
        # =========================

        print(
            f"이번 페이지 새 상품 {added}개"
        )

        print(
            f"현재까지 {len(results)}개"
        )

        # =========================
        # 새 상품 없으면 종료
        # =========================

        if added == 0:

            print(
                "새 상품 없음"
            )

            break

        # =========================
        # 다음 페이지
        # =========================

        page += 1

    # =========================
    # 완료
    # =========================

    print(
        f"다나와 총 {len(results)}개"
    )

    return results


# =========================
# 단독 테스트
# =========================

if __name__ == "__main__":

    query = "T12 인두기"

    # Search.py에서 넘어오는 것과
    # 동일한 형태로 테스트
    options = {
        "api": {
            "sort": "asc"
        }
    }

    results = search_danawa_api(
        query,
        options
    )

    print()

    print(
        "최종 결과 개수:",
        len(results)
    )

    print(
        json.dumps(
            results[:100],
            ensure_ascii=False,
            indent=2
        )
    )