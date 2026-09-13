from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class GlucoseReading(BaseModel):
    timestamp: datetime
    glucose_mg_dl: float


class PredictRequest(BaseModel):
    # The LSTM model consumes exactly 12 points (1h of history at 5-min
    # sampling); the backend always sends that many. min_length=12 catches
    # malformed requests early instead of failing inside the model.
    readings: list[GlucoseReading] = Field(min_length=12)
    horizon_minutes: int = Field(default=30, ge=5, le=60)


class PredictResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    forecast: list[GlucoseReading]
    model_version: str
