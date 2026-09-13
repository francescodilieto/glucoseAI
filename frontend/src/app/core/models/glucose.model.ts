export interface GlucoseReading {
  timestamp: string;
  glucoseMgDl: number;
}

export interface SeriesSummary {
  patientId: string;
  label: string;
  readingCount: number;
}

export interface Series {
  patientId: string;
  readings: GlucoseReading[];
}

export type RiskLevel = 'OK' | 'WARNING' | 'ALERT';

export interface RiskAssessment {
  level: RiskLevel;
  message: string;
}

export interface PredictionResponse {
  patientId: string;
  historical: GlucoseReading[];
  forecast: GlucoseReading[];
  risk: RiskAssessment;
  modelVersion: string;
}
