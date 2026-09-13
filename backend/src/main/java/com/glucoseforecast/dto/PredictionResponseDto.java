package com.glucoseforecast.dto;

import java.util.List;

public record PredictionResponseDto(
        String patientId,
        List<GlucoseReadingDto> historical,
        List<GlucoseReadingDto> forecast,
        RiskAssessmentDto risk,
        String modelVersion
) {
}
