package com.glucoseforecast.dto;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;

public record PredictionRequestDto(
        @NotBlank String patientId,
        @Min(5) @Max(60) Integer horizonMinutes
) {
}
