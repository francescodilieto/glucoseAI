import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { environment } from '../../environments/environment';
import { PredictionResponse, SeriesSummary } from '../core/models/glucose.model';
import { Dashboard } from './dashboard';

describe('Dashboard', () => {
  let httpMock: HttpTestingController;

  const patients: SeriesSummary[] = [
    { patientId: '001', label: 'Patient 001', readingCount: 864 },
    { patientId: '002', label: 'Patient 002', readingCount: 864 },
  ];

  const prediction: PredictionResponse = {
    patientId: '001',
    historical: [{ timestamp: '2024-01-01T08:00:00', glucoseMgDl: 100 }],
    forecast: [{ timestamp: '2024-01-01T08:30:00', glucoseMgDl: 105 }],
    risk: { level: 'OK', message: 'Forecast stays within normal range.' },
    modelVersion: 'naive-trend-v0',
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Dashboard],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();

    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => httpMock.verify());

  it('loads patients and auto-predicts for the first one', () => {
    const fixture = TestBed.createComponent(Dashboard);
    fixture.detectChanges();

    httpMock.expectOne(`${environment.apiBaseUrl}/series`).flush(patients);

    const predictReq = httpMock.expectOne(`${environment.apiBaseUrl}/predict`);
    expect(predictReq.request.body).toEqual({ patientId: '001', horizonMinutes: 30 });
    predictReq.flush(prediction);

    expect(fixture.componentInstance.patients()).toEqual(patients);
    expect(fixture.componentInstance.prediction()).toEqual(prediction);
  });

  it('re-runs the prediction with the new horizon on change', () => {
    const fixture = TestBed.createComponent(Dashboard);
    fixture.detectChanges();

    httpMock.expectOne(`${environment.apiBaseUrl}/series`).flush(patients);
    httpMock.expectOne(`${environment.apiBaseUrl}/predict`).flush(prediction);

    fixture.componentInstance.onHorizonChange(60);

    const predictReq = httpMock.expectOne(`${environment.apiBaseUrl}/predict`);
    expect(predictReq.request.body).toEqual({ patientId: '001', horizonMinutes: 60 });
    predictReq.flush(prediction);
  });
});
