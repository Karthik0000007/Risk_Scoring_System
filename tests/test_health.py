# ── /healthz (Liveness Probe) ──────────────────────────────────────

def test_healthz_returns_200(client):
    response = client.get("/healthz")
    assert response.status_code == 200


def test_healthz_body(client):
    response = client.get("/healthz")
    assert response.json() == {"status": "ok"}


# ── /readyz (Readiness Probe) ──────────────────────────────────────

def test_readyz_returns_200(client):
    response = client.get("/readyz")
    assert response.status_code == 200


def test_readyz_body_includes_model_version(client):
    response = client.get("/readyz")
    assert response.json() == {"ready": True, "model_version": "risk-v1"}


# ── POST /score – Response Structure ──────────────────────────────

def test_score_returns_200(client):
    response = client.post("/score", json={"content": "Hello world"})
    assert response.status_code == 200


def test_score_response_fields(client):
    """Response must contain risk_score, risk_label, and model_version."""
    data = client.post("/score", json={"content": "Sample text"}).json()
    assert "risk_score" in data
    assert "risk_label" in data
    assert "model_version" in data


def test_score_model_version(client):
    data = client.post("/score", json={"content": "Hello"}).json()
    assert data["model_version"] == "risk-v1"


def test_score_not_degraded_when_model_works(client):
    data = client.post("/score", json={"content": "Hello"}).json()
    assert data["degraded"] is False


def test_score_risk_score_range(client):
    """risk_score must be between 0 and 1."""
    data = client.post("/score", json={"content": "Check range"}).json()
    assert 0.0 <= data["risk_score"] <= 1.0


def test_score_risk_label_valid(client):
    """risk_label must be LOW, MEDIUM, HIGH, or UNKNOWN."""
    data = client.post("/score", json={"content": "Check label"}).json()
    assert data["risk_label"] in ("LOW", "MEDIUM", "HIGH", "UNKNOWN")


# ── POST /score – Model Predictions ───────────────────────────────

def test_score_benign_text_is_low(client):
    data = client.post("/score", json={"content": "Have a great day!"}).json()
    assert data["risk_score"] < 0.3
    assert data["risk_label"] == "LOW"


def test_score_spam_text_is_high(client):
    data = client.post(
        "/score",
        json={"content": "WINNER!! You have won a free prize. Call 09061701461 to claim now"},
    ).json()
    assert data["risk_score"] > 0.6
    assert data["risk_label"] == "HIGH"


# ── Input Validation ──────────────────────────────────────────────

def test_score_empty_content_rejected(client):
    """Empty string violates min_length=1 constraint."""
    response = client.post("/score", json={"content": ""})
    assert response.status_code == 422


def test_score_missing_content_rejected(client):
    """Missing 'content' field must return 422."""
    response = client.post("/score", json={})
    assert response.status_code == 422


def test_score_content_too_long_rejected(client):
    """Content exceeding 5000 chars must return 422."""
    response = client.post("/score", json={"content": "x" * 5001})
    assert response.status_code == 422


def test_score_content_at_max_length(client):
    """Content at exactly 5000 chars should be accepted."""
    response = client.post("/score", json={"content": "x" * 5000})
    assert response.status_code == 200


def test_score_content_single_char(client):
    """Single character (min boundary) should be accepted."""
    response = client.post("/score", json={"content": "a"})
    assert response.status_code == 200
