import json
import logging
from datetime import timedelta
from pathlib import Path
from typing import Protocol

import numpy as np

from app.schemas import GlucoseReading

logger = logging.getLogger(__name__)

SAMPLING_INTERVAL_MINUTES = 5
MODELS_DIR = Path(__file__).resolve().parent / "models"


class Predictor(Protocol):
    """Interface every forecasting backend must satisfy."""

    def predict(self, readings: list[GlucoseReading], horizon_minutes: int) -> list[GlucoseReading]:
        ...


class NaiveTrendPredictor:
    """Linear extrapolation of the recent trend.

    This was the original placeholder used to validate the end-to-end wiring
    (Angular -> Spring Boot -> FastAPI) before the LSTM was trained. Kept as
    the fallback if the trained model artifact can't be loaded.
    """

    def __init__(self, lookback_points: int = 12):
        self.lookback_points = lookback_points

    def predict(self, readings: list[GlucoseReading], horizon_minutes: int) -> list[GlucoseReading]:
        recent = readings[-self.lookback_points :]
        x = np.arange(len(recent))
        y = np.array([r.glucose_mg_dl for r in recent])
        slope, intercept = np.polyfit(x, y, deg=1)

        last_timestamp = recent[-1].timestamp
        steps = horizon_minutes // SAMPLING_INTERVAL_MINUTES
        forecast = []
        for step in range(1, steps + 1):
            predicted_value = float(intercept + slope * (len(recent) - 1 + step))
            predicted_value = max(40.0, min(400.0, predicted_value))  # clamp to physiological range
            forecast.append(
                GlucoseReading(
                    timestamp=last_timestamp + timedelta(minutes=SAMPLING_INTERVAL_MINUTES * step),
                    glucose_mg_dl=round(predicted_value, 1),
                )
            )
        return forecast


class LstmPredictor:
    """LSTM trained on the BIG IDEAs Lab CGM dataset (see training/train_lstm.py).

    Consumes the last `lookback_points` glucose readings and predicts the
    next `horizon_points` (60 min at 5-min sampling); shorter requested
    horizons just truncate the output. Runs on onnxruntime, not
    TensorFlow, to keep the serving container light.
    """

    def __init__(self, model_path: Path, scaler_path: Path):
        import onnxruntime as ort  # imported lazily so the naive fallback needs no ML deps at all

        scaler = json.loads(scaler_path.read_text())
        self.lookback_points: int = scaler["lookback_points"]
        self.horizon_points: int = scaler["horizon_points"]
        self.data_min: float = scaler["data_min"]
        self.data_max: float = scaler["data_max"]

        self.session = ort.InferenceSession(str(model_path))
        self.input_name = self.session.get_inputs()[0].name

    def predict(self, readings: list[GlucoseReading], horizon_minutes: int) -> list[GlucoseReading]:
        recent = readings[-self.lookback_points :]
        raw_values = np.array([r.glucose_mg_dl for r in recent], dtype="float32")

        scaled_input = self._scale(raw_values).reshape(1, self.lookback_points, 1)
        scaled_output = self.session.run(None, {self.input_name: scaled_input})[0][0]
        predicted_values = self._inverse_scale(scaled_output)

        steps = min(horizon_minutes // SAMPLING_INTERVAL_MINUTES, self.horizon_points)
        last_timestamp = recent[-1].timestamp
        forecast = []
        for step in range(steps):
            value = float(np.clip(predicted_values[step], 40.0, 400.0))
            forecast.append(
                GlucoseReading(
                    timestamp=last_timestamp + timedelta(minutes=SAMPLING_INTERVAL_MINUTES * (step + 1)),
                    glucose_mg_dl=round(value, 1),
                )
            )
        return forecast

    def _scale(self, values: np.ndarray) -> np.ndarray:
        return (values - self.data_min) / (self.data_max - self.data_min)

    def _inverse_scale(self, scaled_values: np.ndarray) -> np.ndarray:
        return scaled_values * (self.data_max - self.data_min) + self.data_min


def load_predictor() -> tuple[Predictor, str]:
    model_path = MODELS_DIR / "lstm_glucose_forecast.onnx"
    scaler_path = MODELS_DIR / "scaler.json"

    if model_path.exists() and scaler_path.exists():
        try:
            return LstmPredictor(model_path, scaler_path), "lstm-v1"
        except Exception:  # noqa: BLE001 - any load failure should degrade, not crash the service
            logger.exception("Failed to load LSTM model, falling back to naive trend predictor")

    logger.warning("LSTM model artifacts not found at %s, using naive trend predictor", MODELS_DIR)
    return NaiveTrendPredictor(), "naive-trend-v0"
