async function showSettingsPage(mainBox) {
    mainBox.innerHTML = `
        <h1>설정</h1>
        <p>설정 불러오는 중...</p>
    `;

    try {
        const res = await fetch("/Settings");
        const data = await res.json();

        if (data.status !== "ok") {
            mainBox.innerHTML = `
                <h1>설정</h1>
                <p>설정을 불러오지 못했습니다.</p>
            `;
            return;
        }

        renderSettingsLayout(mainBox, data.settings || {});
    } catch (error) {
        console.log("설정 불러오기 실패:", error);

        mainBox.innerHTML = `
            <h1>설정</h1>
            <p>설정을 불러오지 못했습니다.</p>
        `;
    }
}


function renderSettingsLayout(mainBox, settings) {
    const naverSort = settings.naver_sort ?? "asc";
    const naverExclude = settings.naver_exclude ?? "used:cbshop:rental";
    const naverLowestPrice = Number(settings.naver_lowest_price ?? -1);
    const naverPercent = Number(settings.naver_price_tolerance_percent ?? -1);
    const joongmoMonths = Number(settings.joongmo_max_listing_age_months ?? -1);

    mainBox.innerHTML = `
        <h1>설정 화면</h1>

        <div class="settings-box">
            <h2>네이버 설정</h2>

            <div class="settings-row">
                <label for="naverSortSelect">정렬 방식 sort</label>

                <select id="naverSortSelect" class="settings-select">
                    <option value="asc">가격 낮은순</option>
                    <option value="dsc">가격 높은순</option>
                    <option value="sim">정확도순</option>
                    <option value="date">날짜순</option>
                </select>
            </div>

            <div class="settings-row">
                <label for="naverExcludeSelect">제외 조건 exclude</label>

                <select id="naverExcludeSelect" class="settings-select">
                    <option value="">제외 안 함</option>
                    <option value="used">중고 제외</option>
                    <option value="cbshop">해외직구/구매대행 제외</option>
                    <option value="rental">렌탈 상품 제외</option>
                    <option value="used:cbshop">중고 + 해외직구/구매대행 제외</option>
                    <option value="used:rental">중고 + 렌탈 제외</option>
                    <option value="cbshop:rental">해외직구/구매대행 + 렌탈 제외</option>
                    <option value="used:cbshop:rental">중고 + 해외직구/구매대행 + 렌탈 제외</option>
                </select>
            </div>

            ${makeSliderSettingHtml({
                boxId: "lowestPriceBox",
                checkboxId: "lowestPriceCheck",
                inputId: "lowestPriceInput",
                sliderId: "lowestPriceSlider",
                title: "최저가보다 얼마까지 비싸도 허용 사용",
                unit: "원",
                value: naverLowestPrice,
                min: 0,
                max: 1000000,
                step: 10000,
                defaultValue: 0
            })}

            ${makeSliderSettingHtml({
                boxId: "percentBox",
                checkboxId: "percentCheck",
                inputId: "percentInput",
                sliderId: "percentSlider",
                title: "최저가보다 최대 몇 % 비싸도 허용 사용",
                unit: "%",
                value: naverPercent,
                min: 0,
                max: 100,
                step: 1,
                defaultValue: 0
            })}
        </div>

        <div class="settings-box">
            <h2>중고닷 설정</h2>

            ${makeSliderSettingHtml({
                boxId: "monthsBox",
                checkboxId: "monthsCheck",
                inputId: "monthsInput",
                sliderId: "monthsSlider",
                title: "몇 개월 전 매물까지 허용 사용",
                unit: "개월",
                value: joongmoMonths,
                min: 1,
                max: 36,
                step: 1,
                defaultValue: 3
            })}
        </div>

        <button id="settingsSaveButton" class="settings-save-button">
            저장
        </button>
    `;

    document.getElementById("naverSortSelect").value = naverSort;
    document.getElementById("naverExcludeSelect").value = naverExclude;

    setupSliderSetting({
        boxId: "lowestPriceBox",
        checkboxId: "lowestPriceCheck",
        inputId: "lowestPriceInput",
        sliderId: "lowestPriceSlider",
        value: naverLowestPrice,
        defaultValue: 0
    });

    setupSliderSetting({
        boxId: "percentBox",
        checkboxId: "percentCheck",
        inputId: "percentInput",
        sliderId: "percentSlider",
        value: naverPercent,
        defaultValue: 0
    });

    setupSliderSetting({
        boxId: "monthsBox",
        checkboxId: "monthsCheck",
        inputId: "monthsInput",
        sliderId: "monthsSlider",
        value: joongmoMonths,
        defaultValue: 3
    });

    document.getElementById("settingsSaveButton").addEventListener("click", () => {
        saveSettings();
    });
}


function makeSliderSettingHtml(config) {
    const enabled = Number(config.value) !== -1;
    const viewValue = enabled ? Number(config.value) : -1;
    const sliderValue = enabled ? Number(config.value) : config.defaultValue;

    return `
        <div id="${config.boxId}" class="settings-special-box">
            <label class="settings-check-line">
                <input
                    type="checkbox"
                    id="${config.checkboxId}"
                    class="settings-checkbox"
                    ${enabled ? "checked" : ""}
                >
                <span>${config.title}</span>
            </label>

            <div class="settings-slider-row">
                <input
                    type="number"
                    id="${config.inputId}"
                    class="settings-number-input"
                    min="${config.min}"
                    max="${config.max}"
                    step="${config.step}"
                    value="${viewValue}"
                >

                <input
                    type="range"
                    id="${config.sliderId}"
                    class="settings-range"
                    min="${config.min}"
                    max="${config.max}"
                    step="${config.step}"
                    value="${sliderValue}"
                >

                <span class="settings-unit">${config.unit}</span>
            </div>
        </div>
    `;
}


function setupSliderSetting(config) {
    const box = document.getElementById(config.boxId);
    const checkbox = document.getElementById(config.checkboxId);
    const input = document.getElementById(config.inputId);
    const slider = document.getElementById(config.sliderId);

    function refreshState() {
        if (checkbox.checked) {
            box.classList.add("enabled");
            input.disabled = false;
            slider.disabled = false;

            if (Number(input.value) === -1) {
                input.value = config.defaultValue;
                slider.value = config.defaultValue;
            }
        } else {
            box.classList.remove("enabled");
            input.value = -1;
            input.disabled = true;
            slider.disabled = true;
        }
    }

    checkbox.addEventListener("change", () => {
        refreshState();
    });

    slider.addEventListener("input", () => {
        input.value = slider.value;
    });

    input.addEventListener("input", () => {
        if (!checkbox.checked) {
            return;
        }

        let value = Number(input.value || slider.min);
        const min = Number(slider.min);
        const max = Number(slider.max);

        if (value < min) {
            value = min;
        }

        if (value > max) {
            value = max;
        }

        slider.value = value;
    });

    refreshState();
}


function getEnabledNumber(checkboxId, inputId) {
    const checkbox = document.getElementById(checkboxId);
    const input = document.getElementById(inputId);

    if (!checkbox.checked) {
        return -1;
    }

    const value = Number(input.value);

    if (Number.isNaN(value)) {
        return -1;
    }

    return value;
}


async function saveSettings() {
    const saveData = {
        naver_sort: document.getElementById("naverSortSelect").value,
        naver_exclude: document.getElementById("naverExcludeSelect").value,
        naver_lowest_price: getEnabledNumber("lowestPriceCheck", "lowestPriceInput"),
        naver_price_tolerance_percent: getEnabledNumber("percentCheck", "percentInput"),
        joongmo_max_listing_age_months: getEnabledNumber("monthsCheck", "monthsInput")
    };

    try {
        const res = await fetch("/Settings/Save", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(saveData)
        });

        const data = await res.json();

        if (data.status !== "ok") {
            alert(data.message || "설정 저장 실패");
            return;
        }

        alert("설정 저장 완료");
        renderSettingsLayout(document.getElementById("mainBox"), data.settings || saveData);
    } catch (error) {
        console.log("설정 저장 실패:", error);
        alert("설정 저장 실패");
    }
}