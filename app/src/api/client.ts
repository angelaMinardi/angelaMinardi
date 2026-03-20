import axios from 'axios';
import type { GaitFeatures, RiskAssessment, Patient } from '../types';
import { generateMockAssessment } from '../store/mockData';

const API_URL = import.meta.env.VITE_API_URL;

const api = API_URL
  ? axios.create({ baseURL: API_URL, timeout: 10000 })
  : null;

export async function predictRisk(
  features: GaitFeatures
): Promise<RiskAssessment> {
  if (!api) {
    await new Promise((r) => setTimeout(r, 300));
    return generateMockAssessment();
  }
  const { data } = await api.post<RiskAssessment>('/predict', features);
  return data;
}

export async function uploadSession(
  rawData: Record<string, unknown>
): Promise<RiskAssessment> {
  if (!api) {
    await new Promise((r) => setTimeout(r, 500));
    return generateMockAssessment();
  }
  const { data } = await api.post<RiskAssessment>('/upload-session', rawData);
  return data;
}

export async function getPatientHistory(
  patientId: string
): Promise<RiskAssessment[]> {
  if (!api) {
    return [];
  }
  const { data } = await api.get<RiskAssessment[]>(
    `/patient/${patientId}/history`
  );
  return data;
}

export async function getPatientReport(
  patientId: string
): Promise<Record<string, unknown>> {
  if (!api) {
    return {};
  }
  const { data } = await api.get(`/patient/${patientId}/report`);
  return data;
}

export async function getPatients(): Promise<Patient[]> {
  if (!api) {
    return [];
  }
  const { data } = await api.get<Patient[]>('/patients');
  return data;
}

export function isBackendAvailable(): boolean {
  return api !== null;
}
