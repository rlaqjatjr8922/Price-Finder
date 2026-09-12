async function showPartsPage(mainBox) {
    mainBox.innerHTML = `
        <h1>필요한부품</h1>
        <p>부품 목록 불러오는 중...</p>
    `;

    const res = await fetch("/Part");
    const data = await res.json();

    let html = `
        <div class="page-eyebrow">BUILD YOUR PC</div>
        <h1>어떤 부품을 찾으세요?</h1>
        <p class="page-description">필요한 부품을 고르고, 더 좋은 가격을 찾아보세요.</p>
        <div class="selection-heading"><span>부품 선택</span><span id="partCount" aria-live="polite"></span></div>

        <div class="part-list">
    `;

    Object.entries(data.parts).forEach(([partName, isSelected]) => {
        const selectedClass = isSelected ? " selected" : "";

        html += `
            <button 
                class="part-item${selectedClass}"
                data-part-name="${partName}"
                data-selected="${isSelected}"
                aria-pressed="${isSelected}"
            >
                <span class="part-symbol" aria-hidden="true">${selectedPartIcons[partName] || "🔧"}</span>
                <span>${partName}</span><span class="part-check" aria-hidden="true">${isSelected ? "✓" : "+"}</span>
            </button>
        `;
    });

    html += `
        </div>

        <div class="parts-action"><p>다나와 · 중고닷 가격을 한곳에서</p><button class="next-button" id="nextButton">가격 비교하러 가기 <span aria-hidden="true">→</span></button></div>
    `;

    mainBox.innerHTML = html;

    setupPartButtons();
    updatePartCount();
    setupNextButton();
}

function setupPartButtons() {
    const partButtons = document.querySelectorAll(".part-item");

    partButtons.forEach((button) => {
        button.addEventListener("click", async () => {
            const partName = button.dataset.partName;
            const currentValue = button.dataset.selected === "true";
            const newValue = !currentValue;

            const data = {};
            data[partName] = newValue;

            await fetch("/Part/Input", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(data)
            });

            button.dataset.selected = String(newValue);
            button.setAttribute("aria-pressed", String(newValue));
            button.querySelector(".part-check").textContent = newValue ? "✓" : "+";

            if (newValue) {
                button.classList.add("selected");
            } else {
                button.classList.remove("selected");
            }

            console.log("서버로 보냄:", data);
            updatePartCount();
        });
    });
}

function updatePartCount() {
    const count = document.querySelectorAll('.part-item[data-selected="true"]').length;
    const label = document.getElementById("partCount");
    if (label) label.textContent = `${count}개 선택됨`;
}

function setupNextButton() {
    const nextButton = document.getElementById("nextButton");

    if (!nextButton) {
        return;
    }

    nextButton.addEventListener("click", () => {
        showPage("search");
    });
}
