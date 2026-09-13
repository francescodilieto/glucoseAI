package com.glucoseforecast.mlclient;

import com.glucoseforecast.dto.GlucoseReadingDto;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

import java.util.List;

/**
 * Talks to the Python ml-service. Kept as the single place that knows about
 * the ml-service's HTTP contract, so the rest of the backend only deals in
 * {@link GlucoseReadingDto}.
 */
@Component
public class PredictionClient {

    private final RestClient restClient;

    public PredictionClient(RestClient mlServiceRestClient) {
        this.restClient = mlServiceRestClient;
    }

    public Forecast predict(List<GlucoseReadingDto> readings, int horizonMinutes) {
        MlPredictRequest request = new MlPredictRequest(toMlReadings(readings), horizonMinutes);

        MlPredictResponse response = restClient.post()
                .uri("/predict")
                .body(request)
                .retrieve()
                .body(MlPredictResponse.class);

        if (response == null) {
            return new Forecast(List.of(), "unknown");
        }
        return new Forecast(toDtoReadings(response.forecast()), response.modelVersion());
    }

    private List<MlGlucoseReading> toMlReadings(List<GlucoseReadingDto> readings) {
        return readings.stream()
                .map(r -> new MlGlucoseReading(r.timestamp(), r.glucoseMgDl()))
                .toList();
    }

    private List<GlucoseReadingDto> toDtoReadings(List<MlGlucoseReading> readings) {
        return readings.stream()
                .map(r -> new GlucoseReadingDto(r.timestamp(), r.glucoseMgDl()))
                .toList();
    }
}
