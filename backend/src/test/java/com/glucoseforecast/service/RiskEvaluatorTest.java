package com.glucoseforecast.service;

import com.glucoseforecast.dto.GlucoseReadingDto;
import com.glucoseforecast.dto.RiskAssessmentDto.RiskLevel;
import org.junit.jupiter.api.Test;

import java.time.LocalDateTime;
import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;

class RiskEvaluatorTest {

    private final RiskEvaluator riskEvaluator = new RiskEvaluator();
    private final LocalDateTime t0 = LocalDateTime.of(2024, 1, 1, 8, 0);

    @Test
    void flagsAlertWhenForecastDipsBelowHypoglycemiaThreshold() {
        List<GlucoseReadingDto> historical = List.of(reading(0, 90), reading(5, 85));
        List<GlucoseReadingDto> forecast = List.of(reading(10, 75), reading(15, 65));

        var risk = riskEvaluator.evaluate(historical, forecast);

        assertThat(risk.level()).isEqualTo(RiskLevel.ALERT);
    }

    @Test
    void flagsWarningWhenForecastRisesAboveHyperglycemiaThreshold() {
        List<GlucoseReadingDto> historical = List.of(reading(0, 150), reading(5, 160));
        List<GlucoseReadingDto> forecast = List.of(reading(10, 175), reading(15, 185));

        var risk = riskEvaluator.evaluate(historical, forecast);

        assertThat(risk.level()).isEqualTo(RiskLevel.WARNING);
    }

    @Test
    void returnsOkForStableForecastInNormalRange() {
        List<GlucoseReadingDto> historical = List.of(reading(0, 100), reading(5, 101));
        List<GlucoseReadingDto> forecast = List.of(reading(10, 100), reading(15, 99));

        var risk = riskEvaluator.evaluate(historical, forecast);

        assertThat(risk.level()).isEqualTo(RiskLevel.OK);
    }

    private GlucoseReadingDto reading(int minutesFromT0, double glucoseMgDl) {
        return new GlucoseReadingDto(t0.plusMinutes(minutesFromT0), glucoseMgDl);
    }
}
