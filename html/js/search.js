let searchStatusData = {};
let searchProducts = [];
let allSearchProducts = [];

let currentDetailNumber = null;
let selectedGrayButtons = [];

let currentPage = 1;
const pageSize = 100;

let naverDone = false;
let joongmoDone = false;

let currentQuery = "";

let platformCounts = {
    naver: 0,
    joongmo: 0
};


/* =========================================
   검색 화면 표시
========================================= */

async function showSearchPage(mainBox) {
    searchProducts = [];
    allSearchProducts = [];

    currentDetailNumber = null;
    selectedGrayButtons = [];

    currentPage = 1;

    naverDone = false;
    joongmoDone = false;

    platformCounts = {
        naver: 0,
        joongmo: 0
    };

    currentQuery = "";

    mainBox.innerHTML = `
        <h1>검색</h1>
        <p>검색 화면 불러오는 중...</p>
    `;

    try {
        const statusRes = await fetch("/Search");
        const statusData = await statusRes.json();

        searchStatusData =
            statusData.parts ||
            statusData.result ||
            {};

        renderSearchLayout(mainBox);

    } catch (error) {
        console.error("검색 화면 불러오기 실패:", error);

        mainBox.innerHTML = `
            <h1>검색</h1>
            <p>검색 화면을 불러오지 못했습니다.</p>
        `;
    }
}


/* =========================================
   검색 화면 HTML 생성
========================================= */

function renderSearchLayout(mainBox) {
    let partStatusHtml = "";

    Object.entries(searchStatusData).forEach(([partName, value]) => {
        if (value === 0) {
            return;
        }

        const colorClass = value === 2 ? "on" : "off";

        partStatusHtml += `
            <button
                class="search-part-status ${colorClass}"
                disabled
            >
                ${escapeHtml(partName)}
            </button>
        `;
    });


    let saveButtonHtml = "";

    Object.entries(searchStatusData).forEach(([partName, value]) => {
        if (value !== 1) {
            return;
        }

        saveButtonHtml += `
            <button
                class="gray-select-button"
                data-part-name="${escapeHtml(partName)}"
            >
                ${escapeHtml(partName)}
            </button>
        `;
    });


    mainBox.innerHTML = `
        <h1>검색 화면</h1>

        <div class="search-part-status-list">
            ${partStatusHtml}
        </div>


        <div class="search-row">

            <span>검색어</span>

            <input
                type="text"
                id="searchTextInput"
                class="search-text-input"
                placeholder="검색어 입력"
            >

            <button
                id="searchButton"
                class="search-button"
            >
                검색
            </button>

        </div>


        <div
            id="priceFilterBox"
            class="price-filter-box hidden"
        >

            <div class="price-input-row">

                <span>최소가격</span>

                <input
                    type="number"
                    id="minPriceInput"
                    class="price-input"
                    placeholder="최소가격"
                    min="0"
                    value="0"
                >

                <span>최대가격</span>

                <input
                    type="number"
                    id="maxPriceInput"
                    class="price-input"
                    placeholder="최대가격"
                    min="0"
                    value="0"
                >

            </div>


            <div class="range-slider-box">

                <div class="range-slider-track"></div>

                <div
                    id="rangeSliderFill"
                    class="range-slider-fill"
                ></div>

                <input
                    type="range"
                    id="minPriceSlider"
                    class="range-slider range-slider-min"
                    min="0"
                    max="0"
                    step="1000"
                    value="0"
                >

                <input
                    type="range"
                    id="maxPriceSlider"
                    class="range-slider range-slider-max"
                    min="0"
                    max="0"
                    step="1000"
                    value="0"
                >

            </div>


            <div class="price-result-row">

                <span id="priceResultCountText">
                    총 0개의 결과 표시됨
                </span>

            </div>

        </div>


        <div
            id="searchStatusBox"
            class="platform-status-box hidden"
        >

            <div>
                네이버:
                <span id="naverCount">
                    검색중
                </span>
            </div>

            <div>
                중고닷:
                <span id="joongmoCount">
                    검색중
                </span>
            </div>

        </div>


        <div
            id="searchResultControlBox"
            class="hidden"
        >

            <div class="page-row">

                <button id="prevPageButton">
                    이전
                </button>

                <span id="pageInfo">
                    1 ~ 100 / 0
                </span>

                <button id="nextPageButton">
                    다음
                </button>

            </div>


            <div class="search-row">

                <button
                    id="csvCopyButton"
                    class="csv-copy-button"
                >
                    CSV 복사
                </button>

            </div>


            <div class="search-row">

                <span>번호</span>

                <input
                    type="number"
                    id="viewNumberInput"
                    class="view-number-input"
                    placeholder="번호 입력"
                    min="1"
                >

                <button
                    id="viewButton"
                    class="view-button"
                >
                    보기
                </button>

            </div>

        </div>


        <div
            id="detailArea"
            class="hidden"
        >

            <div id="detailCardArea"></div>


            <div class="gray-button-box">

                <p>저장할 부품 선택</p>

                <div class="gray-button-list">
                    ${saveButtonHtml}
                </div>

            </div>


            <button
                id="saveButton"
                class="save-button"
            >
                저장
            </button>

        </div>
    `;

    ensureProductCardStyle();

    setupSearchEvents();
    setupGraySelectButtons();

    updatePageInfo();
    updateRangeSliderFill();
}


/* =========================================
   이벤트 연결
========================================= */

function setupSearchEvents() {
    const searchButton =
        document.getElementById("searchButton");

    const searchTextInput =
        document.getElementById("searchTextInput");

    const csvCopyButton =
        document.getElementById("csvCopyButton");

    const viewButton =
        document.getElementById("viewButton");

    const viewNumberInput =
        document.getElementById("viewNumberInput");

    const saveButton =
        document.getElementById("saveButton");

    const minPriceSlider =
        document.getElementById("minPriceSlider");

    const maxPriceSlider =
        document.getElementById("maxPriceSlider");

    const minPriceInput =
        document.getElementById("minPriceInput");

    const maxPriceInput =
        document.getElementById("maxPriceInput");


    searchButton.addEventListener("click", () => {
        callSearchApi();
    });


    searchTextInput.addEventListener("keydown", (event) => {
        if (event.key === "Enter") {
            callSearchApi();
        }
    });


    csvCopyButton.addEventListener("click", () => {
        copyCsv();
    });


    viewButton.addEventListener("click", () => {
        callSearchDetail();
    });


    viewNumberInput.addEventListener("keydown", (event) => {
        if (event.key === "Enter") {
            callSearchDetail();
        }
    });


    saveButton.addEventListener("click", () => {
        saveDetail();
    });


    minPriceSlider.addEventListener("input", () => {
        syncPriceSlider("min");
    });


    maxPriceSlider.addEventListener("input", () => {
        syncPriceSlider("max");
    });


    minPriceInput.addEventListener("input", () => {
        syncPriceInput("min");
    });


    maxPriceInput.addEventListener("input", () => {
        syncPriceInput("max");
    });


    setupPageButtons();
}


/* =========================================
   검색 실행
========================================= */

async function callSearchApi() {
    const keyword =
        document
            .getElementById("searchTextInput")
            .value
            .trim();

    if (!keyword) {
        alert("검색어를 입력하세요.");
        return;
    }

    currentQuery = keyword;

    searchProducts = [];
    allSearchProducts = [];

    currentDetailNumber = null;
    selectedGrayButtons = [];

    currentPage = 1;

    naverDone = false;
    joongmoDone = false;

    platformCounts = {
        naver: 0,
        joongmo: 0
    };


    document
        .getElementById("detailArea")
        .classList
        .add("hidden");

    document
        .getElementById("searchResultControlBox")
        .classList
        .add("hidden");

    document
        .getElementById("priceFilterBox")
        .classList
        .add("hidden");

    document
        .getElementById("searchStatusBox")
        .classList
        .remove("hidden");


    document.getElementById("naverCount").innerText =
        "검색중";

    document.getElementById("joongmoCount").innerText =
        "검색중";


    updatePageInfo();

    callNaverSearch(keyword);
    callJoongmoSearch(keyword);
}


/* =========================================
   네이버 검색
========================================= */

async function callNaverSearch(keyword) {
    try {
        const res = await fetch("/Search/naver", {
            method: "POST",

            headers: {
                "Content-Type": "text/plain"
            },

            body: keyword
        });


        const data = await res.json();


        if (data.status !== "ok") {
            document.getElementById("naverCount").innerText =
                "실패";

            naverDone = true;

            checkSearchDone();
            return;
        }


        platformCounts.naver =
            data.count || 0;


        document.getElementById("naverCount").innerText =
            platformCounts.naver + "개";


        naverDone = true;

        checkSearchDone();

    } catch (error) {
        console.error("네이버 검색 실패:", error);

        document.getElementById("naverCount").innerText =
            "실패";

        naverDone = true;

        checkSearchDone();
    }
}


/* =========================================
   중고닷 검색
========================================= */

async function callJoongmoSearch(keyword) {
    try {
        const res = await fetch("/Search/joongmo", {
            method: "POST",

            headers: {
                "Content-Type": "text/plain"
            },

            body: keyword
        });


        const data = await res.json();


        if (data.status !== "ok") {
            document.getElementById("joongmoCount").innerText =
                "실패";

            joongmoDone = true;

            checkSearchDone();
            return;
        }


        platformCounts.joongmo =
            data.count || 0;


        document.getElementById("joongmoCount").innerText =
            platformCounts.joongmo + "개";


        joongmoDone = true;

        checkSearchDone();

    } catch (error) {
        console.error("중고닷 검색 실패:", error);

        document.getElementById("joongmoCount").innerText =
            "실패";

        joongmoDone = true;

        checkSearchDone();
    }
}


/* =========================================
   두 검색 완료 확인
========================================= */

async function checkSearchDone() {
    if (!naverDone || !joongmoDone) {
        return;
    }

    await callSearchResult();
}


/* =========================================
   통합 검색 결과 가져오기
========================================= */

async function callSearchResult() {
    try {
        const res = await fetch("/Search/result");
        const data = await res.json();


        if (data.status !== "ok") {
            alert(
                data.message ||
                "최종 검색 결과를 불러오지 못했습니다."
            );

            return;
        }


        allSearchProducts =
            data.products || [];

        searchProducts =
            [...allSearchProducts];

        currentPage = 1;


        document
            .getElementById("searchStatusBox")
            .classList
            .add("hidden");

        document
            .getElementById("searchResultControlBox")
            .classList
            .remove("hidden");

        document
            .getElementById("priceFilterBox")
            .classList
            .remove("hidden");


        setupPriceRangeByProducts();

        updatePageInfo();
        updatePriceResultCount();


        console.log(
            "최종 검색 결과:",
            searchProducts
        );

    } catch (error) {
        console.error(
            "최종 검색 결과 불러오기 실패:",
            error
        );

        alert(
            "최종 검색 결과를 불러오는 중 오류가 발생했습니다."
        );
    }
}


/* =========================================
   페이지 버튼
========================================= */

function setupPageButtons() {
    const prevPageButton =
        document.getElementById("prevPageButton");

    const nextPageButton =
        document.getElementById("nextPageButton");


    prevPageButton.addEventListener("click", () => {
        if (currentPage > 1) {
            currentPage -= 1;

            updatePageInfo();
        }
    });


    nextPageButton.addEventListener("click", () => {
        const maxPage =
            Math.ceil(
                searchProducts.length / pageSize
            );

        if (currentPage < maxPage) {
            currentPage += 1;

            updatePageInfo();
        }
    });
}


/* =========================================
   현재 페이지 표시
========================================= */

function updatePageInfo() {
    const pageInfo =
        document.getElementById("pageInfo");

    if (!pageInfo) {
        return;
    }


    const total =
        searchProducts.length;


    if (total === 0) {
        pageInfo.innerText =
            "1 ~ 100 / 0";

        return;
    }


    const start =
        ((currentPage - 1) * pageSize) + 1;


    let end =
        currentPage * pageSize;


    if (end > total) {
        end = total;
    }


    pageInfo.innerText =
        `${start} ~ ${end} / ${total}`;
}


/* =========================================
   가격을 숫자로 변환
========================================= */

function priceToNumber(value) {
    if (
        value === null ||
        value === undefined
    ) {
        return 0;
    }


    if (typeof value === "number") {
        return value;
    }


    const text =
        String(value);


    if (
        text.includes("나눔") ||
        text.includes("무료")
    ) {
        return 0;
    }


    const numberText =
        text.replace(/[^0-9]/g, "");


    if (numberText === "") {
        return 0;
    }


    return Number(numberText);
}


/* =========================================
   검색 결과 가격 범위 설정
========================================= */

function setupPriceRangeByProducts() {
    const minSlider =
        document.getElementById("minPriceSlider");

    const maxSlider =
        document.getElementById("maxPriceSlider");

    const minInput =
        document.getElementById("minPriceInput");

    const maxInput =
        document.getElementById("maxPriceInput");


    if (allSearchProducts.length === 0) {
        minSlider.min = 0;
        minSlider.max = 0;
        minSlider.value = 0;

        maxSlider.min = 0;
        maxSlider.max = 0;
        maxSlider.value = 0;

        minInput.value = 0;
        maxInput.value = 0;

        updateRangeSliderFill();

        return;
    }


    const prices =
        allSearchProducts
            .map((item) => {
                return priceToNumber(
                    item["가격"]
                );
            })
            .filter((price) => {
                return price >= 0;
            });


    if (prices.length === 0) {
        return;
    }


    const minPrice =
        Math.min(...prices);

    const maxPrice =
        Math.max(...prices);


    const sliderMax =
        maxPrice > minPrice
            ? maxPrice
            : minPrice + 1000;


    const priceStep =
        getPriceStep(
            minPrice,
            sliderMax
        );


    minSlider.min =
        minPrice;

    minSlider.max =
        sliderMax;

    minSlider.step =
        priceStep;

    minSlider.value =
        minPrice;


    maxSlider.min =
        minPrice;

    maxSlider.max =
        sliderMax;

    maxSlider.step =
        priceStep;

    maxSlider.value =
        maxPrice;


    minInput.min =
        minPrice;

    minInput.max =
        sliderMax;

    minInput.value =
        minPrice;


    maxInput.min =
        minPrice;

    maxInput.max =
        sliderMax;

    maxInput.value =
        maxPrice;


    updateRangeSliderFill();
}


/* =========================================
   가격 슬라이더 단위 설정
========================================= */

function getPriceStep(minPrice, maxPrice) {
    const gap =
        maxPrice - minPrice;


    if (gap <= 10000) {
        return 100;
    }


    if (gap <= 100000) {
        return 1000;
    }


    if (gap <= 1000000) {
        return 10000;
    }


    return 50000;
}


/* =========================================
   슬라이더에서 가격 입력창 동기화
========================================= */

function syncPriceSlider(type) {
    const minSlider =
        document.getElementById("minPriceSlider");

    const maxSlider =
        document.getElementById("maxPriceSlider");

    const minInput =
        document.getElementById("minPriceInput");

    const maxInput =
        document.getElementById("maxPriceInput");


    let minValue =
        Number(minSlider.value);

    let maxValue =
        Number(maxSlider.value);


    if (minValue > maxValue) {
        if (type === "min") {
            minValue = maxValue;

            minSlider.value =
                minValue;

        } else {
            maxValue = minValue;

            maxSlider.value =
                maxValue;
        }
    }


    minInput.value =
        minValue;

    maxInput.value =
        maxValue;


    updateRangeSliderFill();
    applyPriceFilter();
}


/* =========================================
   입력창에서 슬라이더 동기화
========================================= */

function syncPriceInput(type) {
    const minSlider =
        document.getElementById("minPriceSlider");

    const maxSlider =
        document.getElementById("maxPriceSlider");

    const minInput =
        document.getElementById("minPriceInput");

    const maxInput =
        document.getElementById("maxPriceInput");


    const sliderMin =
        Number(minSlider.min);

    const sliderMax =
        Number(maxSlider.max);


    let minValue =
        Number(
            minInput.value || sliderMin
        );

    let maxValue =
        Number(
            maxInput.value || sliderMax
        );


    if (minValue < sliderMin) {
        minValue = sliderMin;
    }


    if (minValue > sliderMax) {
        minValue = sliderMax;
    }


    if (maxValue < sliderMin) {
        maxValue = sliderMin;
    }


    if (maxValue > sliderMax) {
        maxValue = sliderMax;
    }


    if (minValue > maxValue) {
        if (type === "min") {
            minValue = maxValue;

            minInput.value =
                minValue;

        } else {
            maxValue = minValue;

            maxInput.value =
                maxValue;
        }
    }


    minSlider.value =
        minValue;

    maxSlider.value =
        maxValue;


    minInput.value =
        minValue;

    maxInput.value =
        maxValue;


    updateRangeSliderFill();
    applyPriceFilter();
}


/* =========================================
   가격 범위 색상 표시
========================================= */

function updateRangeSliderFill() {
    const minSlider =
        document.getElementById("minPriceSlider");

    const maxSlider =
        document.getElementById("maxPriceSlider");

    const fill =
        document.getElementById("rangeSliderFill");


    if (
        !minSlider ||
        !maxSlider ||
        !fill
    ) {
        return;
    }


    const min =
        Number(minSlider.min);

    const max =
        Number(minSlider.max);


    if (max <= min) {
        fill.style.left =
            "0%";

        fill.style.width =
            "100%";

        return;
    }


    const minValue =
        Number(minSlider.value);

    const maxValue =
        Number(maxSlider.value);


    const leftPercent =
        ((minValue - min) / (max - min)) * 100;

    const rightPercent =
        ((maxValue - min) / (max - min)) * 100;


    fill.style.left =
        leftPercent + "%";

    fill.style.width =
        (rightPercent - leftPercent) + "%";
}


/* =========================================
   가격 필터 적용
========================================= */

function applyPriceFilter() {
    if (allSearchProducts.length === 0) {
        return;
    }


    const minInput =
        document
            .getElementById("minPriceInput")
            .value
            .trim();

    const maxInput =
        document
            .getElementById("maxPriceInput")
            .value
            .trim();


    const minSlider =
        document.getElementById("minPriceSlider");

    const maxSlider =
        document.getElementById("maxPriceSlider");


    const sliderMin =
        Number(minSlider.min);

    const sliderMax =
        Number(maxSlider.max);


    const minPrice =
        minInput === ""
            ? sliderMin
            : Number(minInput);

    const maxPrice =
        maxInput === ""
            ? sliderMax
            : Number(maxInput);


    if (minPrice > maxPrice) {
        return;
    }


    searchProducts =
        allSearchProducts.filter((item) => {
            const price =
                priceToNumber(
                    item["가격"]
                );

            return (
                price >= minPrice &&
                price <= maxPrice
            );
        });


    currentPage = 1;


    updatePageInfo();
    updatePriceResultCount();
}


/* =========================================
   필터 결과 개수 표시
========================================= */

function updatePriceResultCount() {
    const text =
        document.getElementById(
            "priceResultCountText"
        );


    if (!text) {
        return;
    }


    text.innerText =
        `총 ${searchProducts.length}개의 결과 표시됨`;
}


/* =========================================
   현재 페이지 CSV 복사
========================================= */

async function copyCsv() {
    if (searchProducts.length === 0) {
        alert("먼저 검색을 완료하세요.");
        return;
    }


    const startIndex =
        (currentPage - 1) * pageSize;

    const endIndex =
        currentPage * pageSize;


    const pageProducts =
        searchProducts.slice(
            startIndex,
            endIndex
        );


    const rows = [];


    rows.push([
        "번호",
        "상품 이름",
        "판매 쇼핑몰 이름",
        "가격"
    ]);


    pageProducts.forEach((item) => {
        rows.push([
            item["번호"],
            item["상품 이름"],
            item["판매 쇼핑몰 이름"],
            item["가격"]
        ]);
    });


    const csvText =
        rows
            .map((row) => {
                return row
                    .map((value) => {
                        const text =
                            String(value ?? "")
                                .replaceAll(
                                    '"',
                                    '""'
                                );

                        return `"${text}"`;
                    })
                    .join(",");
            })
            .join("\n");


    try {
        await navigator.clipboard.writeText(
            csvText
        );

        alert(
            `현재 페이지 ${pageProducts.length}개 CSV 복사 완료`
        );

    } catch (error) {
        console.error(
            "클립보드 복사 실패:",
            error
        );

        fallbackCopyText(csvText);
    }
}


/* =========================================
   클립보드 복사 대체 방법
========================================= */

function fallbackCopyText(text) {
    const textarea =
        document.createElement("textarea");

    textarea.value =
        text;

    textarea.style.position =
        "fixed";

    textarea.style.left =
        "-9999px";

    document.body.appendChild(
        textarea
    );

    textarea.select();

    document.execCommand("copy");

    textarea.remove();

    alert("CSV 복사 완료");
}


/* =========================================
   상세정보 불러오기
========================================= */

async function callSearchDetail() {
    const numberInput =
        document.getElementById(
            "viewNumberInput"
        );

    const number =
        Number(numberInput.value);


    if (!number || number < 1) {
        alert("번호를 입력하세요.");
        return;
    }


    try {
        const res = await fetch(
            "/Search/detail",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "text/plain"
                },

                body: String(number)
            }
        );


        const data =
            await res.json();


        if (data.status !== "ok") {
            alert(
                data.message ||
                "상세정보를 불러오지 못했습니다."
            );

            return;
        }


        currentDetailNumber =
            number;

        selectedGrayButtons =
            [];


        document
            .getElementById("detailArea")
            .classList
            .remove("hidden");


        renderDetail(data.detail);

        resetGrayButtons();


        document
            .getElementById("detailArea")
            .scrollIntoView({
                behavior: "smooth",
                block: "start"
            });

    } catch (error) {
        console.error(
            "상세정보 불러오기 실패:",
            error
        );

        alert(
            "상세정보를 불러오는 중 오류가 발생했습니다."
        );
    }
}


/* =========================================
   HTML 특수문자 처리
========================================= */

function escapeHtml(value) {
    if (
        value === null ||
        value === undefined
    ) {
        return "";
    }


    return String(value)
        .replaceAll(
            "&",
            "&amp;"
        )
        .replaceAll(
            "<",
            "&lt;"
        )
        .replaceAll(
            ">",
            "&gt;"
        )
        .replaceAll(
            '"',
            "&quot;"
        )
        .replaceAll(
            "'",
            "&#039;"
        );
}


/* =========================================
   URL 검증
========================================= */

function safeUrl(value) {
    if (!value) {
        return "";
    }


    const text =
        String(value).trim();


    try {
        const url =
            new URL(
                text,
                window.location.origin
            );


        if (
            url.protocol !== "http:" &&
            url.protocol !== "https:"
        ) {
            return "";
        }


        return url.href;

    } catch (error) {
        return "";
    }
}


/* =========================================
   가격 표시
========================================= */

function formatPrice(value) {
    if (
        typeof value === "string" &&
        (
            value.includes("나눔") ||
            value.includes("무료")
        )
    ) {
        return escapeHtml(value);
    }


    const price =
        priceToNumber(value);


    if (
        Number.isNaN(price) ||
        price < 0
    ) {
        return escapeHtml(value);
    }


    if (price === 0) {
        return "무료나눔";
    }


    return (
        price.toLocaleString("ko-KR") +
        "원"
    );
}


/* =========================================
   날짜 표시 형식
========================================= */

function formatSpecialNote(value) {
    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {
        return "";
    }


    const text =
        String(value);


    const date =
        new Date(text);


    if (Number.isNaN(date.getTime())) {
        return escapeHtml(text);
    }


    return date.toLocaleString(
        "ko-KR",
        {
            year: "numeric",
            month: "2-digit",
            day: "2-digit",
            hour: "2-digit",
            minute: "2-digit"
        }
    );
}


/* =========================================
   상품 카드 상세정보 표시
========================================= */

function renderDetail(detail) {
    const detailCardArea =
        document.getElementById(
            "detailCardArea"
        );


    if (!detailCardArea) {
        return;
    }


    const number =
        escapeHtml(
            detail["번호"]
        );


    const name =
        escapeHtml(
            detail["상품 이름"] ||
            "상품 이름 없음"
        );


    const rawProductLink =
        detail[
            "상품 상세 페이지로 이동하는 링크"
        ];


    const rawImageLink =
        detail["상품 이미지 주소"];


    const productLink =
        safeUrl(rawProductLink);


    const imageLink =
        safeUrl(rawImageLink);


    const specialNote =
        formatSpecialNote(
            detail["특이사항"]
        );


    const mallName =
        escapeHtml(
            detail["판매 쇼핑몰 이름"] ||
            "판매처 정보 없음"
        );


    const price =
        formatPrice(
            detail["가격"]
        );


    const imageHtml =
        imageLink
            ? `
                <img
                    class="product-image"
                    src="${escapeHtml(imageLink)}"
                    alt="${name}"
                    loading="lazy"
                    onerror="
                        this.style.display='none';
                        this.parentElement.classList.add('image-error');
                    "
                >
            `
            : `
                <div class="product-no-image">
                    이미지 없음
                </div>
            `;


    const linkHtml =
        productLink
            ? `
                <a
                    class="product-link"
                    href="${escapeHtml(productLink)}"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    상품 상세 페이지로 이동하기
                </a>
            `
            : `
                <span class="product-link product-link-disabled">
                    상품 상세 페이지 링크 없음
                </span>
            `;


    detailCardArea.innerHTML = `
        <article class="product-card">

            <div class="product-top">

                <section class="product-info">

                    <div class="product-number">
                        상품 번호 ${number}
                    </div>


                    <h2 class="product-name">
                        ${name}
                    </h2>


                    <div class="product-meta">

                        <span>
                            ${mallName}
                        </span>

                        ${
                            specialNote
                                ? `
                                    <span class="product-dot">
                                        ·
                                    </span>

                                    <span>
                                        ${specialNote}
                                    </span>
                                `
                                : ""
                        }

                    </div>


                    <div class="product-price">
                        ${price}
                    </div>

                </section>


                <div class="product-image-box">
                    ${imageHtml}
                </div>

            </div>


            <div class="product-link-box">

                <div class="product-link-icon">
                    ≡
                </div>

                ${linkHtml}

            </div>

        </article>
    `;
}


/* =========================================
   상품 카드 CSS 자동 추가
========================================= */

function ensureProductCardStyle() {
    if (
        document.getElementById(
            "productCardStyle"
        )
    ) {
        return;
    }


    const style =
        document.createElement("style");


    style.id =
        "productCardStyle";


    style.textContent = `
        .product-card {
            width: 100%;
            margin: 30px 0;
            padding: 44px;
            overflow: hidden;
            color: #111111;
            background: #ffffff;
            border: 1px solid #dddddd;
            border-radius: 38px;
        }

        .product-top {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 40px;
        }

        .product-info {
            flex: 1;
            min-width: 0;
        }

        .product-number {
            margin-bottom: 12px;
            color: #888888;
            font-size: 18px;
        }

        .product-name {
            margin: 0;
            color: #111111;
            font-size: 46px;
            line-height: 1.25;
            font-weight: 800;
            overflow-wrap: anywhere;
            word-break: keep-all;
        }

        .product-meta {
            display: flex;
            align-items: center;
            gap: 14px;
            margin-top: 26px;
            color: #777777;
            font-size: 25px;
        }

        .product-dot {
            color: #aaaaaa;
        }

        .product-price {
            margin-top: 34px;
            font-size: 39px;
            font-weight: 800;
        }

        .product-image-box {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 290px;
            min-width: 290px;
            height: 290px;
            overflow: hidden;
            color: #888888;
            background: #eeeeee;
            border-radius: 30px;
        }

        .product-image-box.image-error::after {
            content: "이미지를 불러오지 못했습니다.";
            padding: 20px;
            text-align: center;
        }

        .product-image {
            width: 100%;
            height: 100%;
            display: block;
            object-fit: cover;
        }

        .product-no-image {
            padding: 20px;
            color: #888888;
            font-size: 18px;
            text-align: center;
        }

        .product-link-box {
            display: flex;
            align-items: center;
            gap: 22px;
            margin-top: 44px;
            padding: 32px 36px;
            background: #fff3eb;
            border-radius: 28px;
        }

        .product-link-icon {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 68px;
            min-width: 68px;
            height: 68px;
            color: #ffffff;
            background: #ff6f2c;
            border-radius: 19px;
            font-size: 31px;
            font-weight: 900;
        }

        .product-link {
            min-width: 0;
            overflow: hidden;
            color: #111111;
            font-size: 27px;
            font-weight: 800;
            text-decoration: none;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .product-link:hover {
            text-decoration: underline;
        }

        .product-link-disabled {
            color: #888888;
            cursor: default;
        }

        .product-link-disabled:hover {
            text-decoration: none;
        }

        #detailArea .gray-button-box {
            margin-top: 25px;
        }

        #detailArea .save-button {
            margin-top: 20px;
        }

        @media (max-width: 900px) {
            .product-name {
                font-size: 36px;
            }

            .product-meta {
                font-size: 20px;
            }

            .product-price {
                font-size: 32px;
            }

            .product-image-box {
                width: 240px;
                min-width: 240px;
                height: 240px;
            }

            .product-link {
                font-size: 22px;
            }
        }

        @media (max-width: 750px) {
            .product-card {
                padding: 25px;
                border-radius: 25px;
            }

            .product-top {
                flex-direction: column-reverse;
            }

            .product-image-box {
                width: 100%;
                min-width: 0;
                height: 300px;
            }

            .product-name {
                font-size: 30px;
            }

            .product-meta {
                flex-wrap: wrap;
                font-size: 17px;
            }

            .product-price {
                font-size: 28px;
            }

            .product-link-box {
                gap: 15px;
                margin-top: 25px;
                padding: 20px;
                border-radius: 20px;
            }

            .product-link-icon {
                width: 52px;
                min-width: 52px;
                height: 52px;
                border-radius: 15px;
                font-size: 25px;
            }

            .product-link {
                font-size: 18px;
            }
        }

        @media (max-width: 450px) {
            .product-card {
                padding: 18px;
            }

            .product-image-box {
                height: 240px;
            }

            .product-name {
                font-size: 25px;
            }

            .product-meta {
                font-size: 15px;
            }

            .product-price {
                font-size: 25px;
            }

            .product-link-box {
                padding: 15px;
            }

            .product-link {
                font-size: 15px;
            }
        }
    `;


    document.head.appendChild(
        style
    );
}


/* =========================================
   저장할 부품 버튼
========================================= */

function setupGraySelectButtons() {
    const buttons =
        document.querySelectorAll(
            ".gray-select-button"
        );


    buttons.forEach((button) => {
        button.addEventListener(
            "click",
            () => {
                const partName =
                    button.dataset.partName;


                if (
                    selectedGrayButtons.includes(
                        partName
                    )
                ) {
                    selectedGrayButtons =
                        selectedGrayButtons.filter(
                            (name) => {
                                return name !== partName;
                            }
                        );

                    button.classList.remove(
                        "selected"
                    );

                } else {
                    selectedGrayButtons.push(
                        partName
                    );

                    button.classList.add(
                        "selected"
                    );
                }


                console.log(
                    "선택한 저장 부품:",
                    selectedGrayButtons
                );
            }
        );
    });
}


/* =========================================
   저장 버튼 선택 초기화
========================================= */

function resetGrayButtons() {
    selectedGrayButtons = [];


    const buttons =
        document.querySelectorAll(
            ".gray-select-button"
        );


    buttons.forEach((button) => {
        button.classList.remove(
            "selected"
        );
    });
}


/* =========================================
   상세정보 저장
========================================= */

async function saveDetail() {
    if (currentDetailNumber === null) {
        alert(
            "먼저 번호 입력 후 보기 버튼을 누르세요."
        );

        return;
    }


    if (selectedGrayButtons.length === 0) {
        alert(
            "저장할 부품을 1개 이상 선택하세요."
        );

        return;
    }


    const saveData = {
        number:
            currentDetailNumber,

        query:
            currentQuery,

        selected_buttons:
            selectedGrayButtons
    };


    try {
        const res = await fetch(
            "/Search/Save",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify(
                    saveData
                )
            }
        );


        const data =
            await res.json();


        if (data.status !== "ok") {
            alert(
                data.message ||
                "저장 실패"
            );

            return;
        }


        alert("저장 완료");


        const mainBox =
            document.getElementById(
                "mainBox"
            );


        await showSearchPage(
            mainBox
        );

    } catch (error) {
        console.error(
            "상세정보 저장 실패:",
            error
        );

        alert(
            "저장 중 오류가 발생했습니다."
        );
    }
}