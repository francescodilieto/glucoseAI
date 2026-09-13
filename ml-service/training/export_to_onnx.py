"""
Converts the trained Keras model (app/models/lstm_glucose_forecast.keras)
to ONNX, so the FastAPI ml-service can run inference with onnxruntime alone
-- no TensorFlow needed in the serving container.

Usage: python3 training/export_to_onnx.py
"""

import subprocess
import sys
from pathlib import Path

import tensorflow as tf

MODELS_DIR = Path(__file__).resolve().parent.parent / "app" / "models"
KERAS_PATH = MODELS_DIR / "lstm_glucose_forecast.keras"
SAVED_MODEL_DIR = MODELS_DIR / "_saved_model_tmp"
ONNX_PATH = MODELS_DIR / "lstm_glucose_forecast.onnx"


def main() -> None:
    model = tf.keras.models.load_model(KERAS_PATH)
    model.export(SAVED_MODEL_DIR)

    subprocess.run(
        [
            sys.executable, "-m", "tf2onnx.convert",
            "--saved-model", str(SAVED_MODEL_DIR),
            "--output", str(ONNX_PATH),
            "--opset", "13",
        ],
        check=True,
    )
    print(f"Saved ONNX model to {ONNX_PATH}")


if __name__ == "__main__":
    main()
