import { DatePipe } from '@angular/common';
import { Component, computed, inject, signal } from '@angular/core';

import { GlucoseApiService } from '../core/services/glucose-api.service';
import { PredictionResponse, SeriesSummary } from '../core/models/glucose.model';
import { GlucoseChart } from './glucose-chart/glucose-chart';
import { RiskBadge } from './risk-badge/risk-badge';

const HORIZON_OPTIONS_MINUTES = [15, 30, 45, 60];
const TREND_FLAT_THRESHOLD_MG_DL = 3;

export interface CurrentReading {
  value: number;
  timestamp: string;
  trend: 'up' | 'down' | 'flat';
}

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [DatePipe, GlucoseChart, RiskBadge],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.scss',
})
export class Dashboard {
  private readonly api = inject(GlucoseApiService);

  readonly horizonOptions = HORIZON_OPTIONS_MINUTES;

  readonly patients = signal<SeriesSummary[]>([]);
  readonly selectedPatientId = signal<string | null>(null);
  readonly horizonMinutes = signal(30);
  readonly prediction = signal<PredictionResponse | null>(null);
  readonly loading = signal(false);
  readonly error = signal<string | null>(null);

  readonly currentReading = computed<CurrentReading | null>(() => {
    const historical = this.prediction()?.historical;
    if (!historical || historical.length === 0) {
      return null;
    }
    const last = historical[historical.length - 1];
    const previous = historical[historical.length - 2];
    const delta = previous ? last.glucoseMgDl - previous.glucoseMgDl : 0;

    return {
      value: last.glucoseMgDl,
      timestamp: last.timestamp,
      trend: Math.abs(delta) < TREND_FLAT_THRESHOLD_MG_DL ? 'flat' : delta > 0 ? 'up' : 'down',
    };
  });

  constructor() {
    this.api.listSeries().subscribe({
      next: (patients) => {
        this.patients.set(patients);
        if (patients.length > 0) {
          this.selectedPatientId.set(patients[0].patientId);
          this.runPrediction();
        }
      },
      error: () => this.error.set('Could not reach the backend. Is it running?'),
    });
  }

  onPatientChange(patientId: string): void {
    this.selectedPatientId.set(patientId);
    this.runPrediction();
  }

  onHorizonChange(horizonMinutes: number): void {
    this.horizonMinutes.set(horizonMinutes);
    this.runPrediction();
  }

  runPrediction(): void {
    const patientId = this.selectedPatientId();
    if (!patientId) {
      return;
    }

    this.loading.set(true);
    this.error.set(null);
    this.api.predict(patientId, this.horizonMinutes()).subscribe({
      next: (prediction) => {
        this.prediction.set(prediction);
        this.loading.set(false);
      },
      error: () => {
        this.error.set('Prediction failed. Is the ml-service running?');
        this.loading.set(false);
      },
    });
  }
}
