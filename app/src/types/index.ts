export interface GaitSample {
  timestamp: number;
  fsr: number[];
  accel: [number, number, number];
  gyro: [number, number, number];
  stepCount: number;
  battery: number;
  temperature?: number;
}

export interface GaitFeatures {
  stride_time_mean: number;
  stride_time_cv: number;
  step_time_mean: number;
  step_time_cv: number;
  stance_phase_pct: number;
  swing_phase_pct: number;
  double_support_pct: number;
  cadence: number;
  stride_length_mean: number;
  stride_length_cv: number;
  walking_speed: number;
  peak_pressure_heel: number;
  peak_pressure_midfoot: number;
  peak_pressure_forefoot: number;
  peak_pressure_toe: number;
  cop_displacement_ap: number;
  cop_displacement_ml: number;
  pressure_symmetry_index: number;
  heel_to_toe_transfer_time: number;
  total_ground_reaction_force: number;
  stride_variability_index: number;
  cop_path_length: number;
  sway_rms: number;
  foot_temperature: number;
  step_count: number;
}

export interface RiskAssessment {
  score: number;
  category: 'low' | 'moderate' | 'high';
  timestamp: string;
  topFactors: string[];
}

export interface Patient {
  id: string;
  name: string;
  age: number;
  sex: 'M' | 'F';
  lastReading?: string;
  assessments: RiskAssessment[];
}

export interface DailyTrend {
  date: string;
  riskScore: number;
  steps: number;
  cadence: number;
  walkingSpeed: number;
}

export interface PressureZone {
  name: string;
  value: number;
  x: number;
  y: number;
}

export const FSR_ZONES: PressureZone[] = [
  { name: 'Heel Center', value: 0, x: 50, y: 85 },
  { name: 'Heel Medial', value: 0, x: 35, y: 80 },
  { name: 'Heel Lateral', value: 0, x: 65, y: 80 },
  { name: 'Midfoot Arch', value: 0, x: 40, y: 55 },
  { name: '1st Metatarsal', value: 0, x: 30, y: 30 },
  { name: '3rd Metatarsal', value: 0, x: 50, y: 25 },
  { name: '5th Metatarsal', value: 0, x: 70, y: 30 },
  { name: 'Big Toe', value: 0, x: 30, y: 10 },
];

export type UserRole = 'patient' | 'clinician';
