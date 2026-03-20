import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Cell,
} from 'recharts';
import type { GaitFeatures } from '../../types';

interface Props {
  features: GaitFeatures;
}

interface GaitMetric {
  name: string;
  value: number;
  normLow: number;
  normHigh: number;
  unit: string;
}

function buildMetrics(f: GaitFeatures): GaitMetric[] {
  return [
    { name: 'Cadence', value: f.cadence, normLow: 100, normHigh: 120, unit: 'steps/min' },
    { name: 'Stride Length', value: f.stride_length_mean * 100, normLow: 120, normHigh: 150, unit: 'cm' },
    { name: 'Walking Speed', value: f.walking_speed * 100, normLow: 100, normHigh: 140, unit: 'cm/s' },
    { name: 'Stance Phase', value: f.stance_phase_pct, normLow: 58, normHigh: 62, unit: '%' },
    { name: 'Dbl Support', value: f.double_support_pct, normLow: 10, normHigh: 15, unit: '%' },
    { name: 'Stride CV', value: f.stride_time_cv, normLow: 1, normHigh: 4, unit: '%' },
  ];
}

function barColor(value: number, normLow: number, normHigh: number): string {
  if (value >= normLow && value <= normHigh) return '#22c55e';
  const distance = value < normLow ? normLow - value : value - normHigh;
  const range = normHigh - normLow;
  if (distance < range * 0.5) return '#f59e0b';
  return '#ef4444';
}

export const GaitAnalytics: React.FC<Props> = ({ features }) => {
  const metrics = buildMetrics(features);

  return (
    <div className="bg-white rounded-xl shadow-sm border p-4">
      <h3 className="text-sm font-medium text-gray-500 mb-3">
        Gait Parameters vs. Age-Matched Norms
      </h3>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={metrics} margin={{ top: 10, right: 10, left: -5, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
          <XAxis dataKey="name" tick={{ fontSize: 10 }} stroke="#9ca3af" />
          <YAxis tick={{ fontSize: 10 }} stroke="#9ca3af" />
          <Tooltip
            formatter={(value: number, _name: string, props: { payload: GaitMetric }) => {
              const m = props.payload;
              return [
                `${value.toFixed(1)} ${m.unit} (norm: ${m.normLow}-${m.normHigh})`,
                m.name,
              ];
            }}
            contentStyle={{ borderRadius: 8, border: '1px solid #e5e7eb', fontSize: 12 }}
          />
          {metrics.map((m) => (
            <ReferenceLine
              key={`ref-${m.name}`}
              y={m.normHigh}
              stroke="#94a3b8"
              strokeDasharray="2 2"
              ifOverflow="extendDomain"
            />
          ))}
          <Bar dataKey="value" radius={[4, 4, 0, 0]}>
            {metrics.map((m, i) => (
              <Cell key={i} fill={barColor(m.value, m.normLow, m.normHigh)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <div className="flex items-center gap-4 mt-2 text-xs text-gray-500 justify-center">
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded bg-green-500" /> Within norms
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded bg-amber-500" /> Mildly abnormal
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded bg-red-500" /> Abnormal
        </span>
      </div>
    </div>
  );
};
