package com.glucoseforecast.service;

import com.glucoseforecast.dto.GlucoseReadingDto;
import com.glucoseforecast.dto.PredictionResponseDto;
import com.glucoseforecast.dto.RiskAssessmentDto;
import com.glucoseforecast.mlclient.Forecast;
import com.glucoseforecast.mlclient.PredictionClient;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class PredictionService {

    private static final int DEFAULT_HORIZON_MINUTES = 30;
    private static final int LOOKBACK_POINTS = 12; // last hour at 5-min sampling

    private final DemoSeriesService demoSeriesService;
    private final PredictionClient predictionClient;
    private final RiskEvaluator riskEvaluator;

    public PredictionService(DemoSeriesService demoSeriesService, PredictionClient predictionClient,
                              RiskEvaluator riskEvaluator) {
        this.demoSeriesService = demoSeriesService;
        this.predictionClient = predictionClient;
        this.riskEvaluator = riskEvaluator;
    }

    public PredictionResponseDto predictFor(String patientId, Integer horizonMinutes) {
        int horizon = horizonMinutes != null ? horizonMinutes : DEFAULT_HORIZON_MINUTES;

        List<GlucoseReadingDto> historical = demoSeriesService.getSeries(patientId).readings();
        List<GlucoseReadingDto> recentWindow = historical.subList(
                Math.max(0, historical.size() - LOOKBACK_POINTS), historical.size());

        Forecast forecast = predictionClient.predict(recentWindow, horizon);
        RiskAssessmentDto risk = riskEvaluator.evaluate(historical, forecast.readings());

        return new PredictionResponseDto(patientId, historical, forecast.readings(), risk, forecast.modelVersion());
    }
}
