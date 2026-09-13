from datetime import datetime, timedelta

from fastapi.testclient import TestClient

from app.main import app, MODEL_VERSION

client = TestClient(app)


def _readings(n: int, start_value: float = 100.0, step: float = 1.0):
    start = datetime(2024, 1, 1, 8, 0, 0)
    return [
        {
            "timestamp": (start + timedelta(minutes=5 * i)).isoformat(),
            "glucose_mg_dl": start_value + step * i,
        }
        for i in range(n)
    ]


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_predict_returns_expected_number_of_points():
    payload = {"readings": _readings(12), "horizon_minutes": 30}
    response = client.post("/predict", json=payload)
    assert response.status_code == 200

    body = response.json()
    assert body["model_version"] == MODEL_VERSION
    assert len(body["forecast"]) == 6  # 30 min / 5 min sampling


def test_predict_forecast_is_chronological_and_in_range():
    payload = {"readings": _readings(12), "horizon_minutes": 60}
    response = client.post("/predict", json=payload)
    forecast = response.json()["forecast"]

    assert len(forecast) == 12
    timestamps = [r["timestamp"] for r in forecast]
    assert timestamps == sorted(timestamps)
    assert all(40.0 <= r["glucose_mg_dl"] <= 400.0 for r in forecast)


def test_predict_rejects_too_few_readings():
    payload = {"readings": _readings(5), "horizon_minutes": 30}
    response = client.post("/predict", json=payload)
    assert response.status_code == 422
