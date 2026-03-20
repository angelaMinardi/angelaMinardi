import React from 'react';
import type { RiskAssessment } from '../../types';

interface Props {
  assessment: RiskAssessment;
  size?: number;
}

const COLORS = { low: '#22c55e', moderate: '#f59e0b', high: '#ef4444' };
const LABELS = { low: 'Low Risk', moderate: 'Moderate Risk', high: 'High Risk' };

export const RiskGauge: React.FC<Props> = ({ assessment, size = 200 }) => {
  const { score, category } = assessment;
  const pct = Math.round(score * 100);
  const color = COLORS[category];
  const r = size * 0.38;
  const circumference = 2 * Math.PI * r;
  const dashOffset = circumference * (1 - score * 0.75);

  return (
    <div className="flex flex-col items-center">
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke="#e5e7eb"
          strokeWidth={size * 0.08}
          strokeDasharray={`${circumference * 0.75} ${circumference * 0.25}`}
          strokeLinecap="round"
          transform={`rotate(135 ${size / 2} ${size / 2})`}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke={color}
          strokeWidth={size * 0.08}
          strokeDasharray={`${circumference * 0.75 - dashOffset} ${circumference - (circumference * 0.75 - dashOffset)}`}
          strokeLinecap="round"
          transform={`rotate(135 ${size / 2} ${size / 2})`}
          className="transition-all duration-700"
        />
        <text
          x={size / 2}
          y={size / 2 - 5}
          textAnchor="middle"
          fontSize={size * 0.2}
          fontWeight="bold"
          fill={color}
        >
          {pct}
        </text>
        <text
          x={size / 2}
          y={size / 2 + size * 0.1}
          textAnchor="middle"
          fontSize={size * 0.07}
          fill="#6b7280"
        >
          / 100
        </text>
      </svg>
      <span
        className="mt-1 text-sm font-semibold px-3 py-1 rounded-full"
        style={{ backgroundColor: color + '20', color }}
      >
        {LABELS[category]}
      </span>
    </div>
  );
};
