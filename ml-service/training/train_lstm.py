"""
Trains a small LSTM to forecast the next 60 minutes of CGM glucose from the
last 60 minutes of history, on the BIG IDEAs Lab dataset (see
docs/DATASET.md). Exports the trained model to ONNX for lightweight serving
in the FastAPI ml-service (no TensorFlow needed at inference time).

Usage: python3 training/train_lstm.py
Requires training-data/patient_XXX.csv, produced by
scripts/prepare_training_data.py (run from the repo root first).
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
TRAINING_DATA_DIR = REPO_ROOT / "training-data"
MODELS_DIR = Path(__file__).resolve().parent.parent / "app" / "models"

LOOKBACK_POINTS = 12  # 1 hour of history at 5-min sampling
HORIZON_POINTS = 12  # forecast up to 1 hour ahead; shorter horizons are truncated at serving time
MAX_GAP_MINUTES = 6  # split a patient's series into segments across bigger gaps than this

# Participants never used for training/validation -- held out to measure
# generalization to unseen people.
TEST_PATIENT_IDS = {"014", "015", "016"}


def load_contiguous_segments(csv_path: Path) -> list[np.ndarray]:
    df = pd.read_csv(csv_path, parse_dates=["timestamp"])
    gap_minutes = df["timestamp"].diff().dt.total_seconds() / 60
    segment_id = (gap_minutes > MAX_GAP_MINUTES).cumsum()
    segments = [
        group["glucose_mg_dl"].to_numpy(dtype="float32")
        for _, group in df.groupby(segment_id)
        if len(group) >= LOOKBACK_POINTS + HORIZON_POINTS
    ]
    return segments


def build_windows(segments: list[np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
    inputs, targets = [], []
    for segment in segments:
        for start in range(len(segment) - LOOKBACK_POINTS - HORIZON_POINTS + 1):
            inputs.append(segment[start : start + LOOKBACK_POINTS])
            targets.append(segment[start + LOOKBACK_POINTS : start + LOOKBACK_POINTS + HORIZON_POINTS])
    return np.array(inputs), np.array(targets)


def time_ordered_split(inputs: np.ndarray, targets: np.ndarray, val_fraction: float = 0.15):
    split_at = int(len(inputs) * (1 - val_fraction))
    return inputs[:split_at], targets[:split_at], inputs[split_at:], targets[split_at:]


def build_model() -> tf.keras.Model:
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(LOOKBACK_POINTS, 1)),
        tf.keras.layers.LSTM(64),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(32, activation="relu"),
        tf.keras.layers.Dense(HORIZON_POINTS),
    ])
    model.compile(optimizer="adam", loss="mse", metrics=["mae"])
    return model


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def naive_persistence_baseline(test_inputs: np.ndarray, test_targets: np.ndarray) -> float:
    """Predicts "glucose stays at its last observed value" -- the bar the LSTM must clear."""
    last_values = test_inputs[:, -1:]
    predicted = np.repeat(last_values, HORIZON_POINTS, axis=1)
    return rmse(test_targets, predicted)


def main() -> None:
    train_patient_csvs = [
        p for p in sorted(TRAINING_DATA_DIR.glob("patient_*.csv"))
        if p.stem.split("_")[1] not in TEST_PATIENT_IDS
    ]
    test_patient_csvs = [
        p for p in sorted(TRAINING_DATA_DIR.glob("patient_*.csv"))
        if p.stem.split("_")[1] in TEST_PATIENT_IDS
    ]

    train_segments = [seg for p in train_patient_csvs for seg in load_contiguous_segments(p)]
    test_segments = [seg for p in test_patient_csvs for seg in load_contiguous_segments(p)]

    train_inputs, train_targets = build_windows(train_segments)
    test_inputs, test_targets = build_windows(test_segments)
    train_inputs, train_targets, val_inputs, val_targets = time_ordered_split(train_inputs, train_targets)

    print(f"train windows={len(train_inputs)} val windows={len(val_inputs)} test windows={len(test_inputs)}")

    scaler = MinMaxScaler(feature_range=(0, 1))
    scaler.fit(train_inputs.reshape(-1, 1))

    def scale(x: np.ndarray) -> np.ndarray:
        return scaler.transform(x.reshape(-1, 1)).reshape(x.shape)

    model = build_model()
    model.fit(
        scale(train_inputs)[..., np.newaxis],
        scale(train_targets),
        validation_data=(scale(val_inputs)[..., np.newaxis], scale(val_targets)),
        epochs=50,
        batch_size=64,
        callbacks=[tf.keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True)],
        verbose=2,
    )

    scaled_predictions = model.predict(scale(test_inputs)[..., np.newaxis], verbose=0)
    predictions = scaler.inverse_transform(scaled_predictions.reshape(-1, 1)).reshape(scaled_predictions.shape)

    lstm_rmse = rmse(test_targets, predictions)
    baseline_rmse = naive_persistence_baseline(test_inputs, test_targets)
    print(f"Held-out test RMSE: LSTM={lstm_rmse:.2f} mg/dL, persistence baseline={baseline_rmse:.2f} mg/dL")

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    keras_path = MODELS_DIR / "lstm_glucose_forecast.keras"
    model.save(keras_path)
    print(f"Saved Keras model to {keras_path} (export_to_onnx.py converts this to ONNX)")

    scaler_params = {
        "lookback_points": LOOKBACK_POINTS,
        "horizon_points": HORIZON_POINTS,
        "data_min": float(scaler.data_min_[0]),
        "data_max": float(scaler.data_max_[0]),
    }
    (MODELS_DIR / "scaler.json").write_text(json.dumps(scaler_params, indent=2))

    print(f"Saved model to {MODELS_DIR}")


if __name__ == "__main__":
    main()
