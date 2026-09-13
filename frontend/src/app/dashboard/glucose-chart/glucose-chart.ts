import { AfterViewInit, Component, ElementRef, OnDestroy, effect, input, signal, viewChild } from '@angular/core';
import { Chart, ChartConfiguration, Plugin, registerables } from 'chart.js';

import { GlucoseReading } from '../../core/models/glucose.model';

Chart.register(...registerables);

/** How many of the most recent historical points to plot, to keep the chart readable. */
const VISIBLE_HISTORICAL_POINTS = 60;
const HYPO_THRESHOLD_MG_DL = 70;
const HYPER_THRESHOLD_MG_DL = 180;
const Y_AXIS_MIN = 40;
const Y_AXIS_MAX = 220;

function cssVar(name: string): string {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

function hexToRgba(hex: string, alpha: number): string {
  const value = hex.replace('#', '');
  const r = parseInt(value.substring(0, 2), 16);
  const g = parseInt(value.substring(2, 4), 16);
  const b = parseInt(value.substring(4, 6), 16);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

/**
 * Shades the hypoglycemia (<70 mg/dL) and hyperglycemia (>180 mg/dL) zones
 * behind the data, using the status palette at low opacity -- reference
 * context, not a data series, so it never competes with the lines.
 */
const referenceBandsPlugin: Plugin<'line'> = {
  id: 'referenceBands',
  beforeDatasetsDraw(chart) {
    const { ctx, chartArea } = chart;
    const yScale = chart.scales['y'];
    if (!chartArea || !yScale) {
      return;
    }

    const bands: Array<[number, number, string]> = [
      [yScale.min, HYPO_THRESHOLD_MG_DL, cssVar('--status-critical')],
      [HYPER_THRESHOLD_MG_DL, yScale.max, cssVar('--status-warning')],
    ];

    ctx.save();
    for (const [from, to, color] of bands) {
      const clampedTo = Math.min(to, yScale.max);
      const clampedFrom = Math.max(from, yScale.min);
      if (clampedTo <= clampedFrom) {
        continue;
      }
      const yTop = yScale.getPixelForValue(clampedTo);
      const yBottom = yScale.getPixelForValue(clampedFrom);
      ctx.fillStyle = hexToRgba(color, 0.07);
      ctx.fillRect(chartArea.left, yTop, chartArea.right - chartArea.left, yBottom - yTop);
    }
    ctx.restore();
  },
};

@Component({
  selector: 'app-glucose-chart',
  standalone: true,
  templateUrl: './glucose-chart.html',
  styleUrl: './glucose-chart.scss',
})
export class GlucoseChart implements AfterViewInit, OnDestroy {
  readonly historical = input<GlucoseReading[]>([]);
  readonly forecast = input<GlucoseReading[]>([]);

  private readonly canvasRef = viewChild.required<ElementRef<HTMLCanvasElement>>('canvas');
  private readonly viewReady = signal(false);
  private chart?: Chart;

  constructor() {
    effect(() => {
      if (!this.viewReady()) {
        return;
      }
      this.render(this.historical(), this.forecast());
    });
  }

  ngAfterViewInit(): void {
    this.viewReady.set(true);
  }

  ngOnDestroy(): void {
    this.chart?.destroy();
  }

  private render(historical: GlucoseReading[], forecast: GlucoseReading[]): void {
    const visibleHistorical = historical.slice(-VISIBLE_HISTORICAL_POINTS);
    const historicalColor = cssVar('--series-historical');
    const forecastColor = cssVar('--series-forecast');
    const surfaceColor = cssVar('--surface-card');

    const labels = [...visibleHistorical, ...forecast].map((r) => formatTime(r.timestamp));
    const historicalData: (number | null)[] = [
      ...visibleHistorical.map((r) => r.glucoseMgDl),
      ...forecast.map(() => null),
    ];
    const forecastData: (number | null)[] = [
      ...visibleHistorical.map(() => null),
      ...forecast.map((r) => r.glucoseMgDl),
    ];
    // Bridge the two lines so the forecast visually continues from the last reading.
    if (visibleHistorical.length > 0 && forecast.length > 0) {
      forecastData[visibleHistorical.length - 1] = visibleHistorical[visibleHistorical.length - 1].glucoseMgDl;
    }

    const endDotRadius = (data: (number | null)[]): number[] => {
      const lastNonNullIndex = data.reduce((last, value, i) => (value !== null ? i : last), -1);
      return data.map((value, i) => (i === lastNonNullIndex && value !== null ? 5 : 0));
    };

    const config: ChartConfiguration<'line'> = {
      type: 'line',
      data: {
        labels,
        datasets: [
          {
            label: 'Historical',
            data: historicalData,
            borderColor: historicalColor,
            borderWidth: 2,
            borderCapStyle: 'round',
            borderJoinStyle: 'round',
            pointRadius: endDotRadius(historicalData),
            pointBackgroundColor: historicalColor,
            pointBorderColor: surfaceColor,
            pointBorderWidth: 2,
            fill: false,
            tension: 0.25,
          },
          {
            label: 'Forecast',
            data: forecastData,
            borderColor: forecastColor,
            borderWidth: 2,
            borderCapStyle: 'round',
            borderJoinStyle: 'round',
            borderDash: [6, 4],
            pointRadius: endDotRadius(forecastData),
            pointBackgroundColor: forecastColor,
            pointBorderColor: surfaceColor,
            pointBorderWidth: 2,
            fill: false,
            tension: 0.25,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: false,
        interaction: { mode: 'index', intersect: false },
        plugins: {
          legend: {
            position: 'top',
            align: 'end',
            labels: {
              usePointStyle: true,
              pointStyle: 'circle',
              boxWidth: 8,
              boxHeight: 8,
              color: cssVar('--text-secondary'),
              font: { size: 12 },
            },
          },
          tooltip: {
            backgroundColor: surfaceColor,
            titleColor: cssVar('--text-secondary'),
            bodyColor: cssVar('--text-primary'),
            borderColor: cssVar('--border-hairline'),
            borderWidth: 1,
            cornerRadius: 10,
            padding: 10,
            titleFont: { size: 11, weight: 'normal' },
            bodyFont: { size: 13, weight: 'bold' },
            callbacks: {
              label: (item) => `${item.formattedValue} mg/dL — ${item.dataset.label}`,
            },
          },
        },
        scales: {
          y: {
            min: Y_AXIS_MIN,
            max: Y_AXIS_MAX,
            title: { display: true, text: 'mg/dL', color: cssVar('--text-muted'), font: { size: 11 } },
            grid: { color: cssVar('--gridline') },
            border: { display: false },
            ticks: { color: cssVar('--text-muted'), font: { size: 11 } },
          },
          x: {
            grid: { display: false },
            border: { color: cssVar('--baseline') },
            ticks: { maxTicksLimit: 7, color: cssVar('--text-muted'), font: { size: 11 } },
          },
        },
      },
      plugins: [referenceBandsPlugin],
    };

    if (this.chart) {
      this.chart.data = config.data;
      this.chart.options = config.options!;
      this.chart.update();
    } else {
      this.chart = new Chart(this.canvasRef().nativeElement, config);
    }
  }
}

function formatTime(isoTimestamp: string): string {
  const date = new Date(isoTimestamp);
  return date.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' });
}
