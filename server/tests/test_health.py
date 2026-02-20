from fastapi.testclient import TestClient

from app.main import OFFLINE_HINT, app


def test_health_friendly_offline(monkeypatch):
    async def mock_health():
        return {"online": False, "detail": "connection refused"}

    monkeypatch.setattr("app.main.ollama_client.health", mock_health)

    client = TestClient(app)
    res = client.get("/health")
    assert res.status_code == 200

    payload = res.json()
    assert payload["status"] == "degraded"
    assert payload["ollama_online"] is False
    assert OFFLINE_HINT in payload["message"]
