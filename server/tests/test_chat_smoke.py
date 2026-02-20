import uuid
from pathlib import Path

from fastapi.testclient import TestClient

from app.db import Database
from app.main import app


def test_chat_smoke_saves_sqlite(monkeypatch, tmp_path):
    test_db_path = tmp_path / "chat.db"
    test_db = Database(str(test_db_path))
    monkeypatch.setattr("app.main.db", test_db)

    async def mock_chat(messages, stream=False):
        return "mocked response"

    monkeypatch.setattr("app.main.ollama_client.chat", mock_chat)

    sid = str(uuid.uuid4())
    client = TestClient(app)
    res = client.post(
        "/chat",
        headers={"X-Session-Id": sid},
        json={"message": "Hello", "mode": "auto"},
    )

    assert res.status_code == 200
    payload = res.json()
    assert payload["reply"] == "mocked response"
    assert payload["session_id"] == sid

    history_res = client.get(f"/history/{sid}")
    history = history_res.json()["messages"]
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[1]["role"] == "assistant"
    assert Path(test_db_path).exists()
