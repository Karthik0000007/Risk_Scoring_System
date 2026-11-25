import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def failed_client(monkeypatch):
    """App started with FAIL_MODEL_LOAD=true, so the lifespan load fails."""
    monkeypatch.setenv("FAIL_MODEL_LOAD", "true")
    with TestClient(app) as c:
        yield c


def test_app_starts_when_model_load_fails(failed_client):
    """/healthz stays 200: the process is alive even without a model."""
    response = failed_client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readyz_503_with_reason_when_model_load_fails(failed_client):
    response = failed_client.get("/readyz")
    assert response.status_code == 503
    body = response.json()
    assert body["ready"] is False
    assert "model load failed intentionally" in body["reason"]


def test_score_503_when_model_never_loaded(failed_client):
    response = failed_client.post("/score", json={"content": "hello"})
    assert response.status_code == 503
    assert response.json() == {"detail": "model not loaded"}


def test_model_loaded_gauge_is_zero_when_load_fails(failed_client):
    assert "model_loaded 0.0" in failed_client.get("/metrics").text


def test_readyz_recovers_after_successful_restart(failed_client, monkeypatch):
    """A fresh startup without the failure flag makes the service ready again."""
    monkeypatch.delenv("FAIL_MODEL_LOAD")
    with TestClient(app) as c:
        assert c.get("/readyz").status_code == 200
