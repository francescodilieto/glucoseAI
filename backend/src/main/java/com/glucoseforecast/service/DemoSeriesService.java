package com.glucoseforecast.service;

import com.glucoseforecast.dto.GlucoseReadingDto;
import com.glucoseforecast.dto.SeriesDto;
import com.glucoseforecast.dto.SeriesSummaryDto;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;
import org.springframework.http.HttpStatus;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.time.LocalDateTime;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Loads the bundled demo CGM series (small CSV subset of a public dataset,
 * see docs/DATASET.md) from the classpath. Read-only and in-memory: no
 * database is needed for a handful of demo patients.
 */
@Service
public class DemoSeriesService {

    private static final Map<String, String> DEMO_PATIENTS = Map.of(
            "001", "patient_001.csv",
            "002", "patient_002.csv",
            "003", "patient_003.csv"
    );

    private final Map<String, List<GlucoseReadingDto>> cache = new LinkedHashMap<>();

    public List<SeriesSummaryDto> listSeries() {
        return DEMO_PATIENTS.keySet().stream()
                .map(id -> {
                    List<GlucoseReadingDto> readings = loadReadings(id);
                    return new SeriesSummaryDto(id, "Patient " + id, readings.size());
                })
                .toList();
    }

    public SeriesDto getSeries(String patientId) {
        return new SeriesDto(patientId, loadReadings(patientId));
    }

    private List<GlucoseReadingDto> loadReadings(String patientId) {
        return cache.computeIfAbsent(patientId, this::readCsv);
    }

    private List<GlucoseReadingDto> readCsv(String patientId) {
        String fileName = DEMO_PATIENTS.get(patientId);
        if (fileName == null) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "Unknown patient id: " + patientId);
        }

        ClassPathResource resource = new ClassPathResource("demo-data/" + fileName);
        try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(resource.getInputStream(), StandardCharsets.UTF_8))) {
            return reader.lines()
                    .skip(1) // header
                    .filter(line -> !line.isBlank())
                    .map(this::parseLine)
                    .toList();
        } catch (IOException e) {
            throw new IllegalStateException("Could not read demo data for patient " + patientId, e);
        }
    }

    private GlucoseReadingDto parseLine(String line) {
        String[] parts = line.split(",", 2);
        LocalDateTime timestamp = LocalDateTime.parse(parts[0]);
        double glucoseMgDl = Double.parseDouble(parts[1]);
        return new GlucoseReadingDto(timestamp, glucoseMgDl);
    }
}
