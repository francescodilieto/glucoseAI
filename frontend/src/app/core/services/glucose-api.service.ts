import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { AppConfigService } from './app-config.service';
import { PredictionResponse, Series, SeriesSummary } from '../models/glucose.model';

@Injectable({ providedIn: 'root' })
export class GlucoseApiService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = inject(AppConfigService).apiBaseUrl;

  listSeries(): Observable<SeriesSummary[]> {
    return this.http.get<SeriesSummary[]>(`${this.baseUrl}/series`);
  }

  getSeries(patientId: string): Observable<Series> {
    return this.http.get<Series>(`${this.baseUrl}/series/${patientId}`);
  }

  predict(patientId: string, horizonMinutes: number): Observable<PredictionResponse> {
    return this.http.post<PredictionResponse>(`${this.baseUrl}/predict`, { patientId, horizonMinutes });
  }
}
