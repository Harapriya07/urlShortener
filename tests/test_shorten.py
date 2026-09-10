from app.redis_client import redis_client
def test_shorten_url(client):
    response = client.post(
        "/shorten",
        json={"url": "https://example.com"}
    )

    assert response.status_code == 200

    data = response.json()

    assert "short_code" in data
    assert data["short_code"] is not None

def test_same_url_returns_same_short_code(client):
    url = "https://example.com/same"

    response1 = client.post(
        "/shorten",
        json={"url": url}
    )

    response2 = client.post(
        "/shorten",
        json={"url": url}
    )

    assert response1.status_code == 200
    assert response2.status_code == 200

    assert response1.json()["short_code"] == response2.json()["short_code"]

def test_different_urls_return_different_short_codes(client):
    response1 = client.post(
        "/shorten",
        json={"url": "https://example.com/one"}
    )

    response2 = client.post(
        "/shorten",
        json={"url": "https://example.com/two"}
    )

    assert response1.status_code == 200
    assert response2.status_code == 200

    assert response1.json()["short_code"] != response2.json()["short_code"]

def test_empty_url_is_rejected(client):
    response = client.post(
        "/shorten",
        json={"url": ""}
    )

    assert response.status_code == 422

def test_redirect_short_url(client):
    shorten_response = client.post(
        "/shorten",
        json={"url": "https://example.com/redirect-test"}
    )

    assert shorten_response.status_code == 200

    short_code = shorten_response.json()["short_code"]

    response = client.get(
        f"/{short_code}",
        follow_redirects=False
    )

    assert response.status_code == 307
    assert response.headers["location"] == "https://example.com/redirect-test"

def test_nonexistent_short_url_returns_404(client):
    response = client.get(
        "/doesnotexist",
        follow_redirects=False
    )

    assert response.status_code == 404

def test_click_count_increments(client):
    shorten_response = client.post(
        "/shorten",
        json={"url": "https://example.com/click-test"}
    )

    assert shorten_response.status_code == 200

    short_code = shorten_response.json()["short_code"]

    redis_key = f"clicks:{short_code}"

    redis_client.set(redis_key, 0)

    response = client.get(
        f"/{short_code}",
        follow_redirects=False
    )

    assert response.status_code == 307
    assert int(redis_client.get(redis_key)) == 1


def test_multiple_clicks_are_counted(client):
    shorten_response = client.post(
        "/shorten",
        json={"url": "https://example.com/multiple-clicks"}
    )

    assert shorten_response.status_code == 200

    short_code = shorten_response.json()["short_code"]
    redis_key = f"clicks:{short_code}"

    redis_client.set(redis_key, 0)

    for _ in range(3):
        response = client.get(
            f"/{short_code}",
            follow_redirects=False
        )
        assert response.status_code == 307

    assert int(redis_client.get(redis_key)) == 3



def test_rate_limit(client):

    responses = []

    for _ in range(20):
        response = client.post(
            "/shorten",
            json={"url": "https://example.com/rate-limit-test"}
        )
        responses.append(response.status_code)

    assert 429 in responses

def test_analytics_endpoint(client):
    url = "https://example.com/analytics-test"

    shorten_response = client.post(
        "/shorten",
        json={"url": url}
    )

    assert shorten_response.status_code == 200

    short_code = shorten_response.json()["short_code"]

    response = client.get(
        f"/analytics/{short_code}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["short_code"] == short_code
    assert data["original_url"] == url
    assert data["clicks"] == 0
    assert data["today_clicks"] == 0
    assert len(data["daily_clicks"]) == 7

def test_analytics_after_clicks(client):
    url = "https://example.com/analytics-click-test"

    shorten_response = client.post(
        "/shorten",
        json={"url": url}
    )

    assert shorten_response.status_code == 200

    short_code = shorten_response.json()["short_code"]

    for _ in range(3):
        response = client.get(
            f"/{short_code}",
            follow_redirects=False
        )
        assert response.status_code == 307

    response = client.get(
        f"/analytics/{short_code}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["short_code"] == short_code
    assert data["original_url"] == url
    assert data["today_clicks"] == 3