async function showPartsPage(mainBox) {
    mainBox.innerHTML = `
        <h1>필요한부품</h1>
        <p>부품 목록 불러오는 중...</p>
    `;

    const res = await fetch("/Part");
    const data = await res.json();

    let html = `
        <h1>필요한부품</h1>
        <p>필요한 부품 버튼을 누르세요.</p>

        <div class="part-list">
    `;

    Object.entries(data.parts).forEach(([partName, isSelected]) => {
        const selectedClass = isSelected ? " selected" : "";

        html += `
            <button 
                class="part-item${selectedClass}"
                data-part-name="${partName}"
                data-selected="${isSelected}"
            >
                ${partName}
            </button>
        `;
    });

    html += `
        </div>

        <button class="next-button" id="nextButton">다음</button>
    `;

    mainBox.innerHTML = html;

    setupPartButtons();
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

            if (newValue) {
                button.classList.add("selected");
            } else {
                button.classList.remove("selected");
            }

            console.log("서버로 보냄:", data);
        });
    });
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
