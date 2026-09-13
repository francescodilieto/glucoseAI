package com.glucoseforecast.service;

import com.glucoseforecast.dto.SeriesDto;
import com.glucoseforecast.dto.SeriesSummaryDto;
import org.junit.jupiter.api.Test;
import org.springframework.web.server.ResponseStatusException;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

class DemoSeriesServiceTest {

    private final DemoSeriesService service = new DemoSeriesService();

    @Test
    void listsAllBundledDemoPatients() {
        List<SeriesSummaryDto> series = service.listSeries();

        assertThat(series).hasSize(3);
        assertThat(series).extracting(SeriesSummaryDto::patientId)
                .containsExactlyInAnyOrder("001", "002", "003");
        assertThat(series).allSatisfy(s -> assertThat(s.readingCount()).isGreaterThan(0));
    }

    @Test
    void loadsReadingsInChronologicalOrder() {
        SeriesDto series = service.getSeries("001");

        assertThat(series.readings()).isNotEmpty();
        for (int i = 1; i < series.readings().size(); i++) {
            assertThat(series.readings().get(i).timestamp())
                    .isAfter(series.readings().get(i - 1).timestamp());
        }
    }

    @Test
    void rejectsUnknownPatientId() {
        assertThatThrownBy(() -> service.getSeries("does-not-exist"))
                .isInstanceOf(ResponseStatusException.class);
    }
}
