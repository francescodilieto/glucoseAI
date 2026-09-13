package com.glucoseforecast.mlclient;

import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.List;

public record MlPredictRequest(
        List<MlGlucoseReading> readings,
        @JsonProperty("horizon_minutes") int horizonMinutes
) {
}
