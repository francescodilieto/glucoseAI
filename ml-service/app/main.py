from fastapi import FastAPI

from app.predictor import load_predictor
from app.schemas import PredictRequest, PredictResponse

app = FastAPI(
    title="Glucose Forecast ML Service",
    description="Serves short-term CGM trend forecasts to the Spring Boot backend.",
    version="0.1.0",
)

predictor, MODEL_VERSION = load_predictor()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest) -> PredictResponse:
    forecast = predictor.predict(request.readings, request.horizon_minutes)
    return PredictResponse(forecast=forecast, model_version=MODEL_VERSION)
