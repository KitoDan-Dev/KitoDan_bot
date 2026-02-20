from typing import Dict, List

import httpx


class OllamaClient:
    def __init__(self, base_url: str, model: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def health(self) -> Dict[str, object]:
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                res = await client.get(f"{self.base_url}/api/version")
                res.raise_for_status()
                return {"online": True, "detail": res.json()}
            except httpx.HTTPError:
                try:
                    tags_res = await client.get(f"{self.base_url}/api/tags")
                    tags_res.raise_for_status()
                    return {"online": True, "detail": tags_res.json()}
                except httpx.HTTPError as exc:
                    return {"online": False, "detail": str(exc)}

    async def chat(self, messages: List[Dict[str, str]], stream: bool = False) -> str:
        async with httpx.AsyncClient(timeout=90.0) as client:
            res = await client.post(
                f"{self.base_url}/api/chat",
                json={"model": self.model, "messages": messages, "stream": stream},
            )
            res.raise_for_status()
            data = res.json()
            return data.get("message", {}).get("content", "")
