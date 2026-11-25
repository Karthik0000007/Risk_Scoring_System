def test_index_serves_html_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")


def test_index_has_required_controls(client):
    html = client.get("/").text
    assert "<textarea" in html
    assert 'id="score"' in html
    for example in ("normal", "promo", "phishing"):
        assert f'data-example="{example}"' in html
    assert 'id="degraded"' in html
    assert "503" in html  # explicit not-ready error handling


def test_index_reads_fields_the_api_returns(client):
    """The page's JavaScript must use the real ScoreResponse field names."""
    html = client.get("/").text
    data = client.post("/score", json={"content": "hello"}).json()
    for field in data:
        assert f"data.{field}" in html
