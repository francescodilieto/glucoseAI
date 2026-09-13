package com.glucoseforecast.mlclient;

import com.glucoseforecast.dto.GlucoseReadingDto;

import java.util.List;

public record Forecast(List<GlucoseReadingDto> readings, String modelVersion) {
}
