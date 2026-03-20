import type { Patient, RiskAssessment, DailyTrend, GaitFeatures } from '../types';

function randomBetween(min: number, max: number): number {
  return min + Math.random() * (max - min);
}

export function generateMockAssessment(): RiskAssessment {
  const score = randomBetween(0.15, 0.85);
  const category: RiskAssessment['category'] =
    score < 0.3 ? 'low' : score < 0.7 ? 'moderate' : 'high';
  const allFactors = [
    'Increased stride variability',
    'Reduced walking speed',
    'Asymmetric pressure loading',
    'High medial-lateral sway',
    'Shortened stride length',
    'Elevated stance phase duration',
    'Low foot temperature',
    'Irregular cadence',
  ];
  const topFactors = allFactors.sort(() => Math.random() - 0.5).slice(0, 3);
  return {
    score,
    category,
    timestamp: new Date().toISOString(),
    topFactors,
  };
}

export function generateMockFeatures(): GaitFeatures {
  return {
    stride_time_mean: randomBetween(0.9, 1.3),
    stride_time_cv: randomBetween(2, 12),
    step_time_mean: randomBetween(0.45, 0.65),
    step_time_cv: randomBetween(2, 10),
    stance_phase_pct: randomBetween(55, 68),
    swing_phase_pct: randomBetween(32, 45),
    double_support_pct: randomBetween(10, 25),
    cadence: randomBetween(85, 125),
    stride_length_mean: randomBetween(1.0, 1.6),
    stride_length_cv: randomBetween(2, 10),
    walking_speed: randomBetween(0.6, 1.4),
    peak_pressure_heel: randomBetween(200, 600),
    peak_pressure_midfoot: randomBetween(50, 200),
    peak_pressure_forefoot: randomBetween(150, 500),
    peak_pressure_toe: randomBetween(100, 400),
    cop_displacement_ap: randomBetween(50, 180),
    cop_displacement_ml: randomBetween(10, 60),
    pressure_symmetry_index: randomBetween(0.7, 1.0),
    heel_to_toe_transfer_time: randomBetween(0.2, 0.5),
    total_ground_reaction_force: randomBetween(500, 900),
    stride_variability_index: randomBetween(1, 8),
    cop_path_length: randomBetween(100, 350),
    sway_rms: randomBetween(0.05, 0.4),
    foot_temperature: randomBetween(24, 33),
    step_count: Math.floor(randomBetween(2000, 8000)),
  };
}

function generatePatientHistory(count: number): RiskAssessment[] {
  const assessments: RiskAssessment[] = [];
  for (let i = count - 1; i >= 0; i--) {
    const d = new Date();
    d.setDate(d.getDate() - i);
    const a = generateMockAssessment();
    a.timestamp = d.toISOString();
    assessments.push(a);
  }
  return assessments;
}

export const mockPatients: Patient[] = [
  {
    id: 'p1',
    name: 'Margaret Thompson',
    age: 78,
    sex: 'F',
    lastReading: new Date().toISOString(),
    assessments: generatePatientHistory(30),
  },
  {
    id: 'p2',
    name: 'Robert Chen',
    age: 82,
    sex: 'M',
    lastReading: new Date(Date.now() - 86400000).toISOString(),
    assessments: generatePatientHistory(25),
  },
  {
    id: 'p3',
    name: 'Dorothy Williams',
    age: 71,
    sex: 'F',
    lastReading: new Date(Date.now() - 172800000).toISOString(),
    assessments: generatePatientHistory(20),
  },
  {
    id: 'p4',
    name: 'James Mitchell',
    age: 85,
    sex: 'M',
    lastReading: new Date(Date.now() - 3600000).toISOString(),
    assessments: generatePatientHistory(15),
  },
  {
    id: 'p5',
    name: 'Helen Park',
    age: 74,
    sex: 'F',
    lastReading: new Date(Date.now() - 7200000).toISOString(),
    assessments: generatePatientHistory(28),
  },
];

export const mockTrends: DailyTrend[] = Array.from({ length: 7 }, (_, i) => {
  const d = new Date();
  d.setDate(d.getDate() - (6 - i));
  return {
    date: d.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' }),
    riskScore: Math.round(randomBetween(15, 75)),
    steps: Math.floor(randomBetween(2000, 7000)),
    cadence: Math.round(randomBetween(90, 115)),
    walkingSpeed: parseFloat(randomBetween(0.7, 1.3).toFixed(2)),
  };
});

export function generateMockPressureData(): number[] {
  return [
    randomBetween(300, 600),
    randomBetween(200, 450),
    randomBetween(200, 500),
    randomBetween(50, 180),
    randomBetween(250, 550),
    randomBetween(150, 400),
    randomBetween(100, 350),
    randomBetween(150, 450),
  ];
}
