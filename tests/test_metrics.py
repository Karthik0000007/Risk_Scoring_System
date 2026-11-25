from prometheus_client import REGISTRY

import app.api.score as score_module


def _sample(name, labels=None):
    return REGISTRY.get_sample_value(name, labels or {}) or 0.0


def _raise(_text):
    raise RuntimeError("boom")


def test_metrics_contains_new_names_after_one_score_call(client):
    client.post("/score", json={"content": "Have a great day!"})
    body = client.get("/metrics").text
    assert 'predictions_total{label="LOW"}' in body
    assert "fallback_total" in body
    assert "model_loaded 1.0" in body
    assert 'http_requests_total{method="POST",path="/score",status="200"}' in body


def test_request_metrics_use_route_template_not_raw_url(client):
    client.get("/healthz?probe=123")
    client.get("/does-not-exist/42")
    body = client.get("/metrics").text
    assert 'path="/healthz"' in body
    assert 'path="unmatched"' in body
    assert "/does-not-exist/42" not in body
    assert "probe=123" not in body


def test_metrics_endpoint_is_not_counted(client):
    client.get("/metrics")
    body = client.get("/metrics").text
    assert 'path="/metrics' not in body


def test_prediction_counter_increments_by_label(client):
    before = _sample("predictions_total", {"label": "LOW"})
    client.post("/score", json={"content": "Have a great day!"})
    assert _sample("predictions_total", {"label": "LOW"}) == before + 1


def test_fallback_counter_increments_when_model_fails(client, monkeypatch):
    monkeypatch.setattr(score_module.model, "predict", _raise)
    before = _sample("fallback_total")
    client.post("/score", json={"content": "Urgent: verify your account"})
    assert _sample("fallback_total") == before + 1
