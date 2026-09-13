package com.glucoseforecast.mlclient;

import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.List;

public record MlPredictResponse(
        List<MlGlucoseReading> forecast,
        @JsonProperty("model_version") String modelVersion
) {
}
