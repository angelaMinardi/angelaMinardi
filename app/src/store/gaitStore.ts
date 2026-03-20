import { create } from 'zustand';
import type {
  GaitSample,
  RiskAssessment,
  Patient,
  DailyTrend,
  GaitFeatures,
} from '../types';
import { mockPatients, mockTrends, generateMockAssessment, generateMockFeatures } from './mockData';

interface GaitStore {
  connected: boolean;
  deviceName: string | null;
  battery: number;
  liveSamples: GaitSample[];
  currentRisk: RiskAssessment | null;
  patients: Patient[];
  selectedPatientId: string | null;
  dailyTrends: DailyTrend[];
  latestFeatures: GaitFeatures | null;
  role: 'patient' | 'clinician';

  setConnected: (connected: boolean, deviceName?: string) => void;
  setBattery: (pct: number) => void;
  addSample: (sample: GaitSample) => void;
  setCurrentRisk: (risk: RiskAssessment) => void;
  selectPatient: (id: string) => void;
  setRole: (role: 'patient' | 'clinician') => void;
  refreshMockData: () => void;
}

export const useGaitStore = create<GaitStore>((set) => ({
  connected: false,
  deviceName: null,
  battery: 100,
  liveSamples: [],
  currentRisk: generateMockAssessment(),
  patients: mockPatients,
  selectedPatientId: null,
  dailyTrends: mockTrends,
  latestFeatures: generateMockFeatures(),
  role: 'patient',

  setConnected: (connected, deviceName) =>
    set({ connected, deviceName: deviceName ?? null }),

  setBattery: (battery) => set({ battery }),

  addSample: (sample) =>
    set((state) => ({
      liveSamples: [...state.liveSamples.slice(-500), sample],
      battery: sample.battery,
    })),

  setCurrentRisk: (currentRisk) => set({ currentRisk }),

  selectPatient: (selectedPatientId) => set({ selectedPatientId }),

  setRole: (role) => set({ role }),

  refreshMockData: () =>
    set({
      currentRisk: generateMockAssessment(),
      latestFeatures: generateMockFeatures(),
    }),
}));
