package com.glucoseforecast.controller;

import com.glucoseforecast.dto.PredictionRequestDto;
import com.glucoseforecast.dto.PredictionResponseDto;
import com.glucoseforecast.dto.SeriesDto;
import com.glucoseforecast.dto.SeriesSummaryDto;
import com.glucoseforecast.service.DemoSeriesService;
import com.glucoseforecast.service.PredictionService;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api")
@CrossOrigin // demo project: frontend and backend run on different origins
public class GlucoseController {

    private final DemoSeriesService demoSeriesService;
    private final PredictionService predictionService;

    public GlucoseController(DemoSeriesService demoSeriesService, PredictionService predictionService) {
        this.demoSeriesService = demoSeriesService;
        this.predictionService = predictionService;
    }

    @GetMapping("/series")
    public List<SeriesSummaryDto> listSeries() {
        return demoSeriesService.listSeries();
    }

    @GetMapping("/series/{patientId}")
    public SeriesDto getSeries(@PathVariable String patientId) {
        return demoSeriesService.getSeries(patientId);
    }

    @PostMapping("/predict")
    public PredictionResponseDto predict(@Valid @RequestBody PredictionRequestDto request) {
        return predictionService.predictFor(request.patientId(), request.horizonMinutes());
    }
}
