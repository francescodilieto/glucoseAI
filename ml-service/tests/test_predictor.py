from datetime import datetime, timedelta

import pytest

from app.predictor import MODELS_DIR, LstmPredictor, NaiveTrendPredictor, load_predictor
from app.schemas import GlucoseReading


def _readings(n: int, start_value: float = 100.0, step: float = 1.0):
    start = datetime(2024, 1, 1, 8, 0, 0)
    return [
        GlucoseReading(timestamp=start + timedelta(minutes=5 * i), glucose_mg_dl=start_value + step * i)
        for i in range(n)
    ]


class TestNaiveTrendPredictor:
    def test_extrapolates_rising_trend(self):
        predictor = NaiveTrendPredictor()
        forecast = predictor.predict(_readings(12, start_value=100.0, step=2.0), horizon_minutes=10)

        assert forecast[0].glucose_mg_dl > 120.0
        assert forecast[1].glucose_mg_dl > forecast[0].glucose_mg_dl

    def test_clamps_to_physiological_range(self):
        predictor = NaiveTrendPredictor()
        forecast = predictor.predict(_readings(12, start_value=390.0, step=5.0), horizon_minutes=30)

        assert all(40.0 <= r.glucose_mg_dl <= 400.0 for r in forecast)


@pytest.mark.skipif(
    not (MODELS_DIR / "lstm_glucose_forecast.onnx").exists(),
    reason="trained model artifact not present (run training/train_lstm.py + export_to_onnx.py)",
)
class TestLstmPredictor:
    @pytest.fixture
    def predictor(self):
        return LstmPredictor(MODELS_DIR / "lstm_glucose_forecast.onnx", MODELS_DIR / "scaler.json")

    def test_predicts_full_horizon_at_5min_steps(self, predictor):
        forecast = predictor.predict(_readings(12), horizon_minutes=60)

        assert len(forecast) == 12
        for i in range(1, len(forecast)):
            assert forecast[i].timestamp - forecast[i - 1].timestamp == timedelta(minutes=5)

    def test_truncates_to_requested_horizon(self, predictor):
        forecast = predictor.predict(_readings(12), horizon_minutes=15)
        assert len(forecast) == 3

    def test_output_within_physiological_range(self, predictor):
        forecast = predictor.predict(_readings(12, start_value=110.0, step=0.0), horizon_minutes=60)
        assert all(40.0 <= r.glucose_mg_dl <= 400.0 for r in forecast)


def test_load_predictor_returns_a_usable_predictor():
    predictor, model_version = load_predictor()
    assert model_version in {"lstm-v1", "naive-trend-v0"}
    assert predictor.predict(_readings(12), horizon_minutes=30)
