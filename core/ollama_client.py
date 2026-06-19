import json
import httpx


class OllamaClient:
    def __init__(self, base_url: str, model: str):
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def stream_chat(self, messages: list[dict], stop_event):
        url = f"{self.base_url}/api/generate"

        system_text = ""
        user_text = ""

        for msg in messages:
            role = msg.get("role", "")

            if role == "system":
                system_text += msg.get("content", "") + "\n"

            elif role == "user":
                user_text += msg.get("content", "") + "\n"

        prompt = f"""
{system_text}

규칙:
- 반드시 한국어로만 답하기
- 짧고 자연스럽게 답하기
- 중국어 사용 금지
- 영어 사용 금지

사용자:
{user_text}

Mane:
""".strip()

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": 0.7
            }
        }

        print("=" * 60)
        print("OLLAMA URL:", url)
        print("MODEL:", self.model)
        print("=" * 60)

        async with httpx.AsyncClient(
            timeout=None,
            trust_env=False
        ) as client:

            async with client.stream(
                "POST",
                url,
                json=payload
            ) as response:

                print("STATUS:", response.status_code)

                response.raise_for_status()

                async for line in response.aiter_lines():

                    if stop_event.is_set():
                        break

                    if not line.strip():
                        continue

                    try:
                        data = json.loads(line)

                    except Exception:
                        continue

                    text = data.get("response", "")

                    if text:
                        yield text

                    if data.get("done"):
                        break