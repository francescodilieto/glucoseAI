package com.glucoseforecast.dto;

import java.time.LocalDateTime;

public record GlucoseReadingDto(LocalDateTime timestamp, double glucoseMgDl) {
}
