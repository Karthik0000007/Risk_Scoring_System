import app.api.score as score_module
from app.models.loader import KeywordFallback

fallback = KeywordFallback()


# ── KeywordFallback scoring rules ─────────────────────────────────

def test_benign_text_gets_baseline():
    assert fallback.predict("Have a great day") == 0.05


def test_medium_risk_keywords():
    assert fallback.predict("Urgent: verify your account or it will expire.") == 0.4


def test_high_risk_keywords():
    assert fallback.predict("I will attack and destroy everything and steal it.") > 0.6


def test_score_capped_at_one():
    text = "bomb threat to kill and murder with a weapon, hack and steal"
    assert fallback.predict(text) == 1.0


def test_caps_boost():
    assert fallback.predict("HELLO WORLD") > fallback.predict("hello world")


def test_whole_word_only():
    """'skill' must not match 'kill', 'bankrupt' must not match 'bank'."""
    assert fallback.predict("improve my skill") == 0.05
    assert fallback.predict("bankrupt") == 0.05


def test_multi_word_phrase_matches():
    assert fallback.predict("please click here") == 0.1


def test_matching_is_case_insensitive():
    assert fallback.predict("send me your ssn") == 0.1


# ── /score degraded path ──────────────────────────────────────────

def _raise(_text):
    raise RuntimeError("boom")


def test_model_failure_uses_fallback(client, monkeypatch):
    monkeypatch.setattr(score_module.model, "predict", _raise)
    data = client.post("/score", json={"content": "Urgent: verify your account"}).json()
    assert data["degraded"] is True
    assert data["model_version"] == "keyword-fallback-1.0"
    assert data["risk_score"] == 0.3
    assert data["risk_label"] == "MEDIUM"


def test_model_and_fallback_failure_returns_unknown(client, monkeypatch):
    monkeypatch.setattr(score_module.model, "predict", _raise)
    monkeypatch.setattr(score_module.fallback, "predict", _raise)
    response = client.post("/score", json={"content": "anything"})
    assert response.status_code == 200
    data = response.json()
    assert data["degraded"] is True
    assert data["risk_label"] == "UNKNOWN"
    assert data["risk_score"] == 0.5
