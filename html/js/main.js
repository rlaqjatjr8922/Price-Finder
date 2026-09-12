async function loadLayout() {
    const menuRes = await fetch("menu.html?v=2");
    const screenRes = await fetch("screen.html");

    document.getElementById("menuArea").innerHTML = await menuRes.text();
    document.getElementById("screenArea").innerHTML = await screenRes.text();

    setupMenuButtons();
    showPage("parts");
}

function setupMenuButtons() {
    const buttons = document.querySelectorAll(".menu button");

    buttons.forEach((button) => {
        button.addEventListener("click", () => {
            const page = button.dataset.page;
            showPage(page);
        });
    });
}

async function showPage(page) {
    const mainBox = document.getElementById("mainBox");

    if (!mainBox) {
        console.log("mainBox 없음");
        return;
    }

    document.querySelectorAll(".menu button").forEach((button) => {
        const active = button.dataset.page === page;
        button.classList.toggle("active", active);
        if (active) button.setAttribute("aria-current", "page");
        else button.removeAttribute("aria-current");
    });
    mainBox.dataset.page = page;
    window.scrollTo({ top: 0, behavior: "instant" });

    if (page === "parts") {
        await showPartsPage(mainBox);
        return;
    }

    if (page === "search") {
        await showSearchPage(mainBox);
        return;
    }

    if (page === "selected") {
        await showSelectedPartsPage(mainBox);
        return;
    }

    if (page === "settings") {
        await showSettingsPage(mainBox);
        return;
    }
}

window.addEventListener("DOMContentLoaded", () => {
    loadLayout();
});
