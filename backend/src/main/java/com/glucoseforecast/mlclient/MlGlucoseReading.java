package com.glucoseforecast.mlclient;

import com.fasterxml.jackson.annotation.JsonProperty;

import java.time.LocalDateTime;

/**
 * Mirrors the FastAPI ml-service JSON contract (snake_case), kept separate
 * from {@link com.glucoseforecast.dto.GlucoseReadingDto} so the internal
 * REST API and the ml-service contract can evolve independently.
 */
public record MlGlucoseReading(
        LocalDateTime timestamp,
        @JsonProperty("glucose_mg_dl") double glucoseMgDl
) {
}
