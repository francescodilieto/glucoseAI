package com.glucoseforecast.service;

import com.glucoseforecast.dto.GlucoseReadingDto;
import com.glucoseforecast.dto.RiskAssessmentDto;
import com.glucoseforecast.dto.RiskAssessmentDto.RiskLevel;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * Simple, explainable threshold rules over the forecast — deliberately not
 * another model. Thresholds follow common clinical conventions for CGM
 * alerts (ADA/AACE): below 70 mg/dL is hypoglycemia, above 180 mg/dL is
 * hyperglycemia.
 */
@Service
public class RiskEvaluator {

    private static final double HYPOGLYCEMIA_THRESHOLD = 70.0;
    private static final double HYPERGLYCEMIA_THRESHOLD = 180.0;
    private static final double RAPID_DROP_MG_DL = 20.0;

    public RiskAssessmentDto evaluate(List<GlucoseReadingDto> historical, List<GlucoseReadingDto> forecast) {
        if (forecast.isEmpty()) {
            return new RiskAssessmentDto(RiskLevel.OK, "No forecast available.");
        }

        double minForecast = forecast.stream().mapToDouble(GlucoseReadingDto::glucoseMgDl).min().orElse(Double.NaN);
        double maxForecast = forecast.stream().mapToDouble(GlucoseReadingDto::glucoseMgDl).max().orElse(Double.NaN);

        if (minForecast < HYPOGLYCEMIA_THRESHOLD) {
            return new RiskAssessmentDto(RiskLevel.ALERT,
                    "Forecast dips below %.0f mg/dL — possible hypoglycemia in the next window.".formatted(minForecast));
        }
        if (maxForecast > HYPERGLYCEMIA_THRESHOLD) {
            return new RiskAssessmentDto(RiskLevel.WARNING,
                    "Forecast rises above %.0f mg/dL — trending into hyperglycemia range.".formatted(maxForecast));
        }

        double lastHistorical = historical.isEmpty() ? forecast.get(0).glucoseMgDl() : historical.get(historical.size() - 1).glucoseMgDl();
        double lastForecast = forecast.get(forecast.size() - 1).glucoseMgDl();
        if (lastHistorical - lastForecast >= RAPID_DROP_MG_DL) {
            return new RiskAssessmentDto(RiskLevel.WARNING,
                    "Rapid downward trend detected (%.0f -> %.0f mg/dL).".formatted(lastHistorical, lastForecast));
        }

        return new RiskAssessmentDto(RiskLevel.OK, "Forecast stays within normal range.");
    }
}
