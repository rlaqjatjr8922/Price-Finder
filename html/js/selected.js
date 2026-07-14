const selectedPartOrder = [
    "CPU",
    "메인보드",
    "RAM",
    "그래픽카드",
    "케이스",
    "파워",
    "SSD",
    "HDD",
    "CPU 쿨러",
    "키보드",
    "마우스",
    "모니터"
];


const selectedPartIcons = {
    "CPU": "🖥️",
    "메인보드": "🔲",
    "RAM": "📏",
    "그래픽카드": "🎮",
    "케이스": "🗄️",
    "파워": "⚡",
    "SSD": "💾",
    "HDD": "💽",
    "CPU 쿨러": "🌀",
    "키보드": "⌨️",
    "마우스": "🖱️",
    "모니터": "🖥️"
};


/* =========================================
   선택한 부품 화면 표시
========================================= */

async function showSelectedPartsPage(mainBox) {
    mainBox.innerHTML = `
        <h1>선택한 부품</h1>
        <p>선택한 부품 정보를 불러오는 중...</p>
    `;

    try {
        const res = await fetch("/Selected", {
            method: "GET"
        });

        if (!res.ok) {
            throw new Error(
                `서버 응답 오류: ${res.status}`
            );
        }

        const data = await res.json();

        console.log(
            "/Selected 응답:",
            data
        );

        renderSelectedParts(
            mainBox,
            data
        );

    } catch (error) {
        console.error(
            "선택한 부품 불러오기 실패:",
            error
        );

        mainBox.innerHTML = `
            <h1>선택한 부품</h1>

            <div class="selected-error-box">
                <p>
                    선택한 부품 정보를 불러오지 못했습니다.
                </p>

                <p>
                    ${escapeSelectedHtml(error.message)}
                </p>
            </div>
        `;
    }
}


/* =========================================
   선택한 부품 전체 화면 생성
========================================= */

function renderSelectedParts(
    mainBox,
    selectedData
) {
    const data =
        selectedData &&
        typeof selectedData === "object"
            ? selectedData
            : {};

    let rowsHtml = "";

    selectedPartOrder.forEach(
        (partName, index) => {
            const product =
                data[partName];

            if (
                product &&
                typeof product === "object"
            ) {
                rowsHtml +=
                    makeSelectedProductRow(
                        partName,
                        product,
                        index
                    );
            } else {
                rowsHtml +=
                    makeSelectedEmptyRow(
                        partName,
                        index
                    );
            }
        }
    );

    mainBox.innerHTML = `
        <div class="selected-page">

            <div class="selected-list">
                ${rowsHtml}
            </div>

            <div class="selected-total-box">

                <span class="selected-total-label">
                    총 가격
                </span>

                <strong id="selectedTotalPrice">
                    0원
                </strong>

            </div>

        </div>
    `;

    setupSelectedButtons();
    updateSelectedTotalPrice();
}


/* =========================================
   저장된 상품 행 생성
========================================= */

function makeSelectedProductRow(
    partName,
    product,
    index
) {
    const productName =
        escapeSelectedHtml(
            product["상품 이름"] ||
            "상품 이름 없음"
        );

    const productLink =
        makeSelectedSafeUrl(
            product[
                "상품 상세 페이지로 이동하는 링크"
            ]
        );

    const imageLink =
        makeSelectedSafeUrl(
            product["상품 이미지 주소"]
        );

    const mallName =
        escapeSelectedHtml(
            product["판매 쇼핑몰 이름"] ||
            ""
        );

    const quantity =
        normalizeSelectedQuantity(
            product["구매수량"]
        );

    const unitPrice =
        selectedPriceToNumber(
            product["가격"]
        );

    const totalPrice =
        unitPrice * quantity;

    const icon =
        selectedPartIcons[partName] ||
        "🔧";


    const imageHtml = imageLink
        ? productLink
            ? `
                <a
                    class="selected-row-image-link"
                    href="${escapeSelectedHtml(productLink)}"
                    target="_blank"
                    rel="noopener noreferrer"
                    title="상품 페이지 열기"
                >
                    <img
                        class="selected-row-image"
                        src="${escapeSelectedHtml(imageLink)}"
                        alt="${productName}"
                        loading="lazy"
                        onerror="
                            this.style.display='none';
                            this.parentElement.parentElement.classList.add('image-error');
                        "
                    >
                </a>
            `
            : `
                <img
                    class="selected-row-image"
                    src="${escapeSelectedHtml(imageLink)}"
                    alt="${productName}"
                    loading="lazy"
                    onerror="
                        this.style.display='none';
                        this.parentElement.classList.add('image-error');
                    "
                >
            `
        : `
            <span class="selected-no-image">
                이미지 없음
            </span>
        `;


    const productNameHtml =
        productLink
            ? `
                <a
                    class="selected-row-product-name"
                    href="${escapeSelectedHtml(productLink)}"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    ${productName}
                </a>
            `
            : `
                <span class="selected-row-product-name">
                    ${productName}
                </span>
            `;


    return `
        <div
            class="selected-row selected-row-filled"
            data-part-name="${escapeSelectedHtml(partName)}"
            data-unit-price="${unitPrice}"
        >

            <div class="selected-part-label">

                <span class="selected-part-number">
                    ${index + 1}
                </span>

                <span class="selected-part-icon">
                    ${icon}
                </span>

                <strong class="selected-part-name">
                    ${escapeSelectedHtml(partName)}
                </strong>

            </div>


            <div class="selected-product-area">

                <div class="selected-row-image-box">
                    ${imageHtml}
                </div>


                <div class="selected-product-text">

                    ${productNameHtml}

                    ${
                        mallName
                            ? `
                                <span class="selected-row-mall">
                                    ${mallName}
                                </span>
                            `
                            : ""
                    }

                </div>


                <div class="selected-quantity-box">

                    <button
                        type="button"
                        class="
                            selected-quantity-button
                            selected-minus-button
                        "
                        data-part-name="${escapeSelectedHtml(partName)}"
                    >
                        −
                    </button>

                    <span class="selected-quantity-value">
                        ${quantity}
                    </span>

                    <button
                        type="button"
                        class="
                            selected-quantity-button
                            selected-plus-button
                        "
                        data-part-name="${escapeSelectedHtml(partName)}"
                    >
                        ＋
                    </button>

                </div>


                <div class="selected-price-area">

                    <span class="selected-price-label">
                        판매가
                    </span>

                    <strong class="selected-row-price">
                        ${formatSelectedTotalPrice(totalPrice)}
                    </strong>

                </div>


                <button
                    type="button"
                    class="selected-remove-button"
                    data-part-name="${escapeSelectedHtml(partName)}"
                    title="상품 삭제"
                >
                    ×
                </button>

            </div>

        </div>
    `;
}


/* =========================================
   상품이 없는 부품 행 생성
========================================= */

function makeSelectedEmptyRow(
    partName,
    index
) {
    const icon =
        selectedPartIcons[partName] ||
        "🔧";

    return `
        <div
            class="selected-row selected-row-empty"
            data-part-name="${escapeSelectedHtml(partName)}"
        >

            <div class="selected-part-label">

                <span class="selected-part-number">
                    ${index + 1}
                </span>

                <span class="selected-part-icon">
                    ${icon}
                </span>

                <strong class="selected-part-name">
                    ${escapeSelectedHtml(partName)}
                </strong>

            </div>


            <div
                class="
                    selected-product-area
                    selected-empty-product-area
                "
            >
                상품을 선택해주세요.
            </div>

        </div>
    `;
}


/* =========================================
   −, ＋, × 버튼 이벤트 연결
========================================= */

function setupSelectedButtons() {
    const minusButtons =
        document.querySelectorAll(
            ".selected-minus-button"
        );

    const plusButtons =
        document.querySelectorAll(
            ".selected-plus-button"
        );

    const removeButtons =
        document.querySelectorAll(
            ".selected-remove-button"
        );


    minusButtons.forEach((button) => {
        button.addEventListener(
            "click",
            async () => {
                const partName =
                    button.dataset.partName;

                await changeSelectedQuantity(
                    partName,
                    -1,
                    button
                );
            }
        );
    });


    plusButtons.forEach((button) => {
        button.addEventListener(
            "click",
            async () => {
                const partName =
                    button.dataset.partName;

                await changeSelectedQuantity(
                    partName,
                    1,
                    button
                );
            }
        );
    });


    removeButtons.forEach((button) => {
        button.addEventListener(
            "click",
            async () => {
                const partName =
                    button.dataset.partName;

                await deleteSelectedPart(
                    partName,
                    button
                );
            }
        );
    });
}


/* =========================================
   구매수량 변경 요청
========================================= */

async function changeSelectedQuantity(
    partName,
    change,
    clickedButton
) {
    const row =
        clickedButton.closest(
            ".selected-row-filled"
        );

    if (!row) {
        return;
    }

    const quantityElement =
        row.querySelector(
            ".selected-quantity-value"
        );

    const currentQuantity =
        normalizeSelectedQuantity(
            quantityElement.textContent
        );

    if (
        change === -1 &&
        currentQuantity <= 1
    ) {
        return;
    }

    setSelectedRowDisabled(
        row,
        true
    );

    try {
        const res = await fetch(
            "/Selected/Quantity",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    part_name: partName,
                    change: change
                })
            }
        );

        if (!res.ok) {
            throw new Error(
                `서버 응답 오류: ${res.status}`
            );
        }

        const data =
            await res.json();

        if (data.status !== "ok") {
            alert(
                data.message ||
                "수량 변경 실패"
            );

            return;
        }

        const newQuantity =
            normalizeSelectedQuantity(
                data["구매수량"] ??
                data.quantity
            );

        quantityElement.textContent =
            newQuantity;

        const unitPrice =
            Number(
                row.dataset.unitPrice || 0
            );

        const priceElement =
            row.querySelector(
                ".selected-row-price"
            );

        priceElement.textContent =
            formatSelectedTotalPrice(
                unitPrice * newQuantity
            );

        updateSelectedTotalPrice();

        console.log(
            "구매수량 변경 완료:",
            {
                part_name: partName,
                change: change,
                구매수량: newQuantity
            }
        );

    } catch (error) {
        console.error(
            "구매수량 변경 실패:",
            error
        );

        alert(
            "구매수량 변경 중 오류가 발생했습니다."
        );

    } finally {
        setSelectedRowDisabled(
            row,
            false
        );
    }
}


/* =========================================
   선택한 상품 삭제 요청
========================================= */

async function deleteSelectedPart(
    partName,
    clickedButton
) {
    const confirmed =
        confirm(
            `${partName}에 저장된 상품을 삭제할까요?`
        );

    if (!confirmed) {
        return;
    }

    const row =
        clickedButton.closest(
            ".selected-row-filled"
        );

    if (row) {
        setSelectedRowDisabled(
            row,
            true
        );
    }

    try {
        const res = await fetch(
            "/Selected/Delete",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    part_name: partName
                })
            }
        );

        if (!res.ok) {
            throw new Error(
                `서버 응답 오류: ${res.status}`
            );
        }

        const data =
            await res.json();

        if (data.status !== "ok") {
            alert(
                data.message ||
                "상품 삭제 실패"
            );

            if (row) {
                setSelectedRowDisabled(
                    row,
                    false
                );
            }

            return;
        }

        console.log(
            "상품 삭제 완료:",
            partName
        );

        const mainBox =
            document.getElementById(
                "mainBox"
            );

        await showSelectedPartsPage(
            mainBox
        );

    } catch (error) {
        console.error(
            "상품 삭제 요청 실패:",
            error
        );

        alert(
            "상품 삭제 중 오류가 발생했습니다."
        );

        if (row) {
            setSelectedRowDisabled(
                row,
                false
            );
        }
    }
}


/* =========================================
   전체 총 가격 계산
========================================= */

function updateSelectedTotalPrice() {
    const totalPriceElement =
        document.getElementById(
            "selectedTotalPrice"
        );

    if (!totalPriceElement) {
        return;
    }

    const rows =
        document.querySelectorAll(
            ".selected-row-filled"
        );

    let totalPrice = 0;

    rows.forEach((row) => {
        const unitPrice =
            Number(
                row.dataset.unitPrice || 0
            );

        const quantityElement =
            row.querySelector(
                ".selected-quantity-value"
            );

        const quantity =
            normalizeSelectedQuantity(
                quantityElement?.textContent
            );

        totalPrice +=
            unitPrice * quantity;
    });

    totalPriceElement.textContent =
        totalPrice.toLocaleString(
            "ko-KR"
        ) + "원";
}


/* =========================================
   요청 중 버튼 잠금
========================================= */

function setSelectedRowDisabled(
    row,
    disabled
) {
    const buttons =
        row.querySelectorAll(
            "button"
        );

    buttons.forEach((button) => {
        button.disabled =
            disabled;
    });

    if (disabled) {
        row.classList.add(
            "selected-row-loading"
        );
    } else {
        row.classList.remove(
            "selected-row-loading"
        );
    }
}


/* =========================================
   구매수량 정리
========================================= */

function normalizeSelectedQuantity(value) {
    const quantity =
        Number(value);

    if (
        !Number.isInteger(quantity) ||
        quantity < 1
    ) {
        return 1;
    }

    return quantity;
}


/* =========================================
   가격을 숫자로 변환
========================================= */

function selectedPriceToNumber(value) {
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
        text.includes("무료") ||
        text.includes("나눔")
    ) {
        return 0;
    }

    const numberText =
        text.replace(
            /[^0-9]/g,
            ""
        );

    if (numberText === "") {
        return 0;
    }

    return Number(numberText);
}


/* =========================================
   가격 표시
========================================= */

function formatSelectedTotalPrice(price) {
    const number =
        Number(price);

    if (
        Number.isNaN(number) ||
        number <= 0
    ) {
        return "무료나눔";
    }

    return (
        number.toLocaleString("ko-KR") +
        "원"
    );
}


/* =========================================
   HTML 특수문자 처리
========================================= */

function escapeSelectedHtml(value) {
    if (
        value === null ||
        value === undefined
    ) {
        return "";
    }

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


/* =========================================
   안전한 URL 확인
========================================= */

function makeSelectedSafeUrl(value) {
    if (!value) {
        return "";
    }

    try {
        const url =
            new URL(
                String(value).trim(),
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