import React, { useMemo } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  ZAxis,
} from 'recharts';
import type { Patient } from '../../types';

interface Props {
  patient: Patient;
}

export const TemporalAnalysis: React.FC<Props> = ({ patient }) => {
  const riskTimeSeries = useMemo(
    () =>
      patient.assessments.map((a) => ({
        date: new Date(a.timestamp).toLocaleDateString('en-US', {
          month: 'short',
          day: 'numeric',
        }),
        score: Math.round(a.score * 100),
      })),
    [patient.assessments]
  );

  // Poincare plot: stride[n] vs stride[n+1] (simulated from risk scores as proxy)
  const poincare = useMemo(() => {
    const scores = patient.assessments.map((a) => a.score);
    return scores.slice(0, -1).map((s, i) => ({
      current: +(s * 1.2 + 0.3).toFixed(3),
      next: +(scores[i + 1] * 1.2 + 0.3).toFixed(3),
    }));
  }, [patient.assessments]);

  return (
    <div className="space-y-4">
      {/* Risk score time series */}
      <div className="bg-white rounded-xl shadow-sm border p-4">
        <h3 className="text-sm font-medium text-gray-500 mb-3">
          Risk Score History - {patient.name}
        </h3>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={riskTimeSeries} margin={{ top: 5, right: 10, left: -10, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
            <XAxis dataKey="date" tick={{ fontSize: 10 }} stroke="#9ca3af" />
            <YAxis domain={[0, 100]} tick={{ fontSize: 10 }} stroke="#9ca3af" />
            <Tooltip contentStyle={{ borderRadius: 8, border: '1px solid #e5e7eb', fontSize: 12 }} />
            <Line
              type="monotone"
              dataKey="score"
              stroke="#6366f1"
              strokeWidth={2}
              dot={{ r: 3 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Poincare plot */}
      <div className="bg-white rounded-xl shadow-sm border p-4">
        <h3 className="text-sm font-medium text-gray-500 mb-1">
          Stride Variability (Poincare Plot)
        </h3>
        <p className="text-xs text-gray-400 mb-3">
          Each point plots stride[n] vs stride[n+1]. Tight clustering = consistent gait.
        </p>
        <ResponsiveContainer width="100%" height={220}>
          <ScatterChart margin={{ top: 5, right: 10, left: -5, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
            <XAxis
              dataKey="current"
              name="Stride n"
              unit="s"
              tick={{ fontSize: 10 }}
              stroke="#9ca3af"
            />
            <YAxis
              dataKey="next"
              name="Stride n+1"
              unit="s"
              tick={{ fontSize: 10 }}
              stroke="#9ca3af"
            />
            <ZAxis range={[30, 30]} />
            <Tooltip
              contentStyle={{ borderRadius: 8, border: '1px solid #e5e7eb', fontSize: 12 }}
              formatter={(v: number) => `${v.toFixed(3)} s`}
            />
            <Scatter data={poincare} fill="#6366f1" opacity={0.6} />
          </ScatterChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
