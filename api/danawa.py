import requests
from bs4 import BeautifulSoup
from urllib.parse import quote


def search_danawa_shop(query, sort="asc", exclude=None):
    results = []
    seen = set()
    page = 1

    while True:
        print(f"다나와 {page}페이지 검색중...")

        url = (
            "https://search.danawa.com/dsearch.php"
            f"?query={quote(query)}"
            f"&page={page}"
        )

        html = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        ).text

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        items = soup.select(
            "li.prod_item"
        )

        if not items:
            print("상품 없음")
            break

        added = 0

        for item in items:
            title_tag = item.select_one(
                "p.prod_name > a"
            )

            price_tag = item.select_one(
                'input[id^="min_price_"]'
            )

            if not title_tag or not price_tag:
                continue

            product_id = item.get("id")

            if product_id in seen:
                continue

            seen.add(product_id)

            image_tag = item.select_one(
                ".thumb_image img"
            )

            image = None

            if image_tag:
                image = (
                    image_tag.get("data-original")
                    or image_tag.get("data-src")
                    or image_tag.get("src")
                )

                if image and image.startswith("//"):
                    image = "https:" + image

            price = price_tag.get("value")

            results.append({
                "title": title_tag.get_text(
                    " ",
                    strip=True
                ),
                "link": title_tag.get("href"),
                "image": image,
                "price": price,
                "teugisahang": price,
                "mallName": "다나와"
            })

            added += 1

        print(
            f"이번 페이지 새 상품 {added}개"
        )

        print(
            f"현재까지 {len(results)}개"
        )

        if added == 0:
            print("새 상품 없음")
            break

        page += 1

    if sort == "asc":
        results.sort(
            key=lambda x: int(x["price"])
        )

    elif sort == "dsc":
        results.sort(
            key=lambda x: int(x["price"]),
            reverse=True
        )

    print(
        f"다나와 총 {len(results)}개"
    )

    return results


if __name__ == "__main__":
    query = input(
        "다나와 검색어: "
    ).strip()

    results = search_danawa_shop(
        query
    )

    print()
    print(
        "최종 결과 개수:",
        len(results)
    )

    for item in results[:20]:
        print(
            item["price"],
            item["title"]
        )