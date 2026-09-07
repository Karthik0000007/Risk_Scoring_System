from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# ── /healthz (Liveness Probe) ──────────────────────────────────────

def test_healthz_returns_200():
    response = client.get("/healthz")
    assert response.status_code == 200


def test_healthz_body():
    response = client.get("/healthz")
    assert response.json() == {"status": "ok"}


# ── /readyz (Readiness Probe) ──────────────────────────────────────

def test_readyz_returns_200():
    response = client.get("/readyz")
    assert response.status_code == 200


def test_readyz_body():
    response = client.get("/readyz")
    assert response.json() == {"ready": True}


# ── POST /score – Response Structure ──────────────────────────────

def test_score_returns_200():
    response = client.post("/score", json={"content": "Hello world"})
    assert response.status_code == 200


def test_score_response_fields():
    """Response must contain risk_score, risk_label, and model_version."""
    data = client.post("/score", json={"content": "Sample text"}).json()
    assert "risk_score" in data
    assert "risk_label" in data
    assert "model_version" in data


def test_score_model_version():
    data = client.post("/score", json={"content": "Hello"}).json()
    assert data["model_version"] == "heuristic-1.0.0"


def test_score_risk_score_range():
    """risk_score must be between 0 and 1."""
    data = client.post("/score", json={"content": "Check range"}).json()
    assert 0.0 <= data["risk_score"] <= 1.0


def test_score_risk_label_valid():
    """risk_label must be LOW, MEDIUM, HIGH, or UNKNOWN."""
    data = client.post("/score", json={"content": "Check label"}).json()
    assert data["risk_label"] in ("LOW", "MEDIUM", "HIGH", "UNKNOWN")


# ── POST /score – Heuristic Risk Levels ───────────────────────────

def test_score_benign_text_is_low():
    """Friendly text with no risk keywords should score LOW."""
    data = client.post("/score", json={"content": "Have a great day!"}).json()
    assert data["risk_score"] < 0.3
    assert data["risk_label"] == "LOW"


def test_score_medium_risk_keywords():
    """Phishing-style urgency keywords should score MEDIUM."""
    data = client.post(
        "/score",
        json={"content": "Urgent: verify your account or it will expire."},
    ).json()
    assert 0.3 <= data["risk_score"] <= 0.6
    assert data["risk_label"] == "MEDIUM"


def test_score_high_risk_keywords():
    """Threat / violence keywords should score HIGH."""
    data = client.post(
        "/score",
        json={"content": "I will attack and destroy everything and steal your credentials."},
    ).json()
    assert data["risk_score"] > 0.6
    assert data["risk_label"] == "HIGH"


def test_score_critical_keywords_very_high():
    """Multiple critical keywords should push the score very high."""
    data = client.post(
        "/score",
        json={"content": "bomb threat to kill and murder with a weapon"},
    ).json()
    assert data["risk_score"] > 0.8
    assert data["risk_label"] == "HIGH"


def test_score_caps_boost():
    """Excessive uppercase text adds to the risk score."""
    data_normal = client.post("/score", json={"content": "hello world"}).json()
    data_caps = client.post("/score", json={"content": "HELLO WORLD"}).json()
    assert data_caps["risk_score"] > data_normal["risk_score"]


def test_score_capped_at_one():
    """Score must never exceed 1.0 even with many keyword hits."""
    data = client.post(
        "/score",
        json={
            "content": (
                "kill bomb attack murder shoot destroy terror explode weapon "
                "hack steal fraud phishing malware ransomware exploit breach "
                "urgent verify suspend click here act now DANGER!!!"
            )
        },
    ).json()
    assert data["risk_score"] <= 1.0


# ── Input Validation ──────────────────────────────────────────────

def test_score_empty_content_rejected():
    """Empty string violates min_length=1 constraint."""
    response = client.post("/score", json={"content": ""})
    assert response.status_code == 422


def test_score_missing_content_rejected():
    """Missing 'content' field must return 422."""
    response = client.post("/score", json={})
    assert response.status_code == 422


def test_score_content_too_long_rejected():
    """Content exceeding 5000 chars must return 422."""
    response = client.post("/score", json={"content": "x" * 5001})
    assert response.status_code == 422


def test_score_content_at_max_length():
    """Content at exactly 5000 chars should be accepted."""
    response = client.post("/score", json={"content": "x" * 5000})
    assert response.status_code == 200


def test_score_content_single_char():
    """Single character (min boundary) should be accepted."""
    response = client.post("/score", json={"content": "a"})
    assert response.status_code == 200
