package com.glucoseforecast.dto;

public record RiskAssessmentDto(RiskLevel level, String message) {

    public enum RiskLevel {
        OK, WARNING, ALERT
    }
}
