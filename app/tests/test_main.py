from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health_returns_200():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_metrics_endpoint_exposes_prometheus_format():
    # Сначала делаем запрос, чтобы счётчик точно увеличился
    client.get("/api/v1/health")

    response = client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text
    assert 'endpoint="/api/v1/health"' in response.text


def test_post_data_echoes_payload():
    payload = {"name": "test", "value": 42}
    response = client.post("/api/v1/data", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["received"] == payload
    assert 1 <= body["random_value"] <= 100


def test_get_item_by_id():
    response = client.get("/api/v1/data/7")
    assert response.status_code == 200
    assert response.json() == {"id": 7, "value": "item_7"}


def test_get_item_rejects_non_integer_id():
    response = client.get("/api/v1/data/abc")
    assert response.status_code == 422


def test_list_items_pagination():
    response = client.get("/api/v1/data", params={"limit": 5, "offset": 10})
    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 5
    assert body["items"][0]["id"] == 10
    assert body["limit"] == 5
    assert body["offset"] == 10
