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

        renderSettingsLayout(
            mainBox,
            data.settings || {}
        );

    } catch (error) {
        console.log(
            "설정 불러오기 실패:",
            error
        );

        mainBox.innerHTML = `
            <h1>설정</h1>
            <p>설정을 불러오지 못했습니다.</p>
        `;
    }
}


function renderSettingsLayout(
    mainBox,
    settings
) {
    const danawaSort =
        settings.danawa_sort ?? "asc";

    const joongmoMonths = Number(
        settings.joongmo_max_listing_age_months ?? -1
    );

    mainBox.innerHTML = `
        <div class="page-eyebrow">MAKE IT YOURS</div>
        <h1>내게 맞는 검색 설정</h1>
        <p class="page-description">검색할 사이트를 켜거나 끈 뒤 저장해 주세요.</p>

        <div class="settings-box">
            <div class="provider-heading"><h2>다나와 설정</h2>
                <label class="provider-toggle">
                    <input type="checkbox" role="switch" id="danawaEnabled" aria-label="다나와 검색 사용" ${settings.danawa_enabled !== false ? "checked" : ""}>
                    <span class="toggle-track" aria-hidden="true"></span>
                    <span class="toggle-state" aria-hidden="true"></span>
                </label>
            </div>

            <div class="settings-row">
                <label for="danawaSortSelect">
                    정렬 방식
                </label>

                <select
                    id="danawaSortSelect"
                    class="settings-select"
                >
                    <option value="asc">
                        가격 낮은순
                    </option>

                    <option value="desc">
                        가격 높은순
                    </option>
                </select>
            </div>
        </div>

        <div class="settings-box">
            <div class="provider-heading"><h2>중고닷 설정</h2>
                <label class="provider-toggle">
                    <input type="checkbox" role="switch" id="joongmoEnabled" aria-label="중고닷 검색 사용" ${settings.joongmo_enabled !== false ? "checked" : ""}>
                    <span class="toggle-track" aria-hidden="true"></span>
                    <span class="toggle-state" aria-hidden="true"></span>
                </label>
            </div>

            ${makeSliderSettingHtml({
                boxId: "monthsBox",
                checkboxId: "monthsCheck",
                inputId: "monthsInput",
                sliderId: "monthsSlider",
                title: "몇 개월 전 매물까지 허용",
                unit: "개월",
                value: joongmoMonths,
                min: 1,
                max: 36,
                step: 1,
                defaultValue: 3
            })}
        </div>

        <button
            id="settingsSaveButton"
            class="settings-save-button"
        >
            저장
        </button>
    `;

    document.getElementById(
        "danawaSortSelect"
    ).value = danawaSort;

    setupSliderSetting({
        boxId: "monthsBox",
        checkboxId: "monthsCheck",
        inputId: "monthsInput",
        sliderId: "monthsSlider",
        value: joongmoMonths,
        defaultValue: 3
    });

    document.getElementById(
        "settingsSaveButton"
    ).addEventListener(
        "click",
        saveSettings
    );
}


function makeSliderSettingHtml(
    config
) {
    const enabled =
        Number(config.value) !== -1;

    const viewValue =
        enabled
            ? Number(config.value)
            : -1;

    const sliderValue =
        enabled
            ? Number(config.value)
            : config.defaultValue;

    return `
        <div
            id="${config.boxId}"
            class="settings-special-box"
        >
            <label
                class="settings-check-line"
            >
                <input
                    type="checkbox"
                    id="${config.checkboxId}"
                    class="settings-checkbox"
                    ${enabled ? "checked" : ""}
                >

                <span>
                    ${config.title}
                </span>
            </label>

            <div class="settings-slider-row">
                <input
                    type="number"
                    id="${config.inputId}"
                    aria-label="${config.title} (${config.unit})"
                    inputmode="numeric"
                    class="settings-number-input"
                    min="${config.min}"
                    max="${config.max}"
                    step="${config.step}"
                    value="${viewValue}"
                >

                <input
                    type="range"
                    id="${config.sliderId}"
                    aria-label="${config.title} 조절"
                    class="settings-range"
                    min="${config.min}"
                    max="${config.max}"
                    step="${config.step}"
                    value="${sliderValue}"
                >

                <span class="settings-unit">
                    ${config.unit}
                </span>
            </div>
        </div>
    `;
}


function setupSliderSetting(
    config
) {
    const box =
        document.getElementById(
            config.boxId
        );

    const checkbox =
        document.getElementById(
            config.checkboxId
        );

    const input =
        document.getElementById(
            config.inputId
        );

    const slider =
        document.getElementById(
            config.sliderId
        );

    function refreshState() {
        if (checkbox.checked) {
            box.classList.add(
                "enabled"
            );

            input.disabled = false;
            slider.disabled = false;

            if (
                Number(input.value) === -1
            ) {
                input.value =
                    config.defaultValue;

                slider.value =
                    config.defaultValue;
            }

        } else {
            box.classList.remove(
                "enabled"
            );

            input.value = -1;
            input.disabled = true;
            slider.disabled = true;
        }
    }

    checkbox.addEventListener(
        "change",
        () => {
            refreshState();
        }
    );

    slider.addEventListener(
        "input",
        () => {
            input.value =
                slider.value;
        }
    );

    input.addEventListener(
        "input",
        () => {
            if (!checkbox.checked) {
                return;
            }

            let value = Number(
                input.value
                || slider.min
            );

            const min = Number(
                slider.min
            );

            const max = Number(
                slider.max
            );

            if (value < min) {
                value = min;
            }

            if (value > max) {
                value = max;
            }

            slider.value = value;
        }
    );

    refreshState();
}


function getEnabledNumber(
    checkboxId,
    inputId
) {
    const checkbox =
        document.getElementById(
            checkboxId
        );

    const input =
        document.getElementById(
            inputId
        );

    if (!checkbox.checked) {
        return -1;
    }

    const value = Number(
        input.value
    );

    if (Number.isNaN(value)) {
        return -1;
    }

    return value;
}


async function saveSettings() {
    const saveData = {
        danawa_enabled: document.getElementById("danawaEnabled").checked,
        joongmo_enabled: document.getElementById("joongmoEnabled").checked,
        danawa_sort:
            document.getElementById(
                "danawaSortSelect"
            ).value,

        joongmo_max_listing_age_months:
            getEnabledNumber(
                "monthsCheck",
                "monthsInput"
            )
    };

    try {
        const res = await fetch(
            "/Settings/Save",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body:
                    JSON.stringify(
                        saveData
                    )
            }
        );

        const data =
            await res.json();

        if (data.status !== "ok") {
            alert(
                data.message
                || "설정 저장 실패"
            );

            return;
        }

        alert(
            "설정 저장 완료"
        );

        renderSettingsLayout(
            document.getElementById(
                "mainBox"
            ),
            data.settings
            || saveData
        );

    } catch (error) {
        console.log(
            "설정 저장 실패:",
            error
        );

        alert(
            "설정 저장 실패"
        );
    }
}
