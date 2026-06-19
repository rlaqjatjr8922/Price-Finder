const chat = document.getElementById("chat");
const statusBox = document.getElementById("status");
const face = document.getElementById("face");
const input = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendBtn");
const stopBtn = document.getElementById("stopBtn");
const regenBtn = document.getElementById("regenBtn");

let ws = null;
let currentAssistantMsg = null;

function addMessage(role, text) {
    const div = document.createElement("div");
    div.className = `msg ${role}`;
    div.textContent = text;
    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
    return div;
}

function setStatus(text) {
    statusBox.textContent = text;
}

function connect() {
    const protocol = location.protocol === "https:" ? "wss" : "ws";
    ws = new WebSocket(`${protocol}://${location.host}/client-ws`);

    ws.onopen = () => {
        setStatus("연결됨");
        addMessage("system", "Mane 서버 연결됨");
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.type === "init") {
            face.textContent = data.face || ">o<";
        }

        if (data.type === "status") {
            if (data.status === "thinking") setStatus("생각중...");
            if (data.status === "done") setStatus("완료");
            if (data.status === "stopped") setStatus("중지됨");
        }

        if (data.type === "assistant_start") {
            face.textContent = data.face || ">o<";
            currentAssistantMsg = addMessage("assistant", "");
        }

        if (data.type === "assistant_delta") {
            if (!currentAssistantMsg) currentAssistantMsg = addMessage("assistant", "");
            currentAssistantMsg.textContent += data.text;
            chat.scrollTop = chat.scrollHeight;
        }

        if (data.type === "error") {
            setStatus("오류");
            addMessage("error", "오류: " + data.message);
        }
    };

    ws.onclose = () => {
        setStatus("연결 끊김. 2초 뒤 재연결");
        setTimeout(connect, 2000);
    };

    ws.onerror = () => {
        setStatus("WebSocket 오류");
    };
}

function sendMessage() {
    const text = input.value.trim();
    if (!text || !ws || ws.readyState !== WebSocket.OPEN) return;

    addMessage("user", text);
    currentAssistantMsg = null;
    ws.send(JSON.stringify({ type: "chat", text }));
    input.value = "";
}

sendBtn.onclick = sendMessage;

input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendMessage();
});

stopBtn.onclick = () => {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: "stop" }));
    }
};

regenBtn.onclick = () => {
    if (ws && ws.readyState === WebSocket.OPEN) {
        currentAssistantMsg = null;
        ws.send(JSON.stringify({ type: "regenerate" }));
    }
};

connect();
