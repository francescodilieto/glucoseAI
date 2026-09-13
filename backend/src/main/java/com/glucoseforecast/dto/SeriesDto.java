package com.glucoseforecast.dto;

import java.util.List;

public record SeriesDto(String patientId, List<GlucoseReadingDto> readings) {
}
