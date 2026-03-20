import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import type { DailyTrend } from '../../types';

interface Props {
  data: DailyTrend[];
  dataKey?: keyof DailyTrend;
  label?: string;
  color?: string;
  showThresholds?: boolean;
}

export const TrendChart: React.FC<Props> = ({
  data,
  dataKey = 'riskScore',
  label = 'Fall Risk Score',
  color = '#6366f1',
  showThresholds = true,
}) => {
  return (
    <div className="bg-white rounded-xl shadow-sm border p-4">
      <h3 className="text-sm font-medium text-gray-500 mb-3">{label}</h3>
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={data} margin={{ top: 5, right: 10, left: -10, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
          <XAxis dataKey="date" tick={{ fontSize: 11 }} stroke="#9ca3af" />
          <YAxis tick={{ fontSize: 11 }} stroke="#9ca3af" domain={[0, 100]} />
          <Tooltip
            contentStyle={{
              borderRadius: 8,
              border: '1px solid #e5e7eb',
              fontSize: 13,
            }}
          />
          {showThresholds && (
            <>
              <ReferenceLine y={30} stroke="#22c55e" strokeDasharray="4 4" />
              <ReferenceLine y={70} stroke="#ef4444" strokeDasharray="4 4" />
            </>
          )}
          <Line
            type="monotone"
            dataKey={dataKey}
            stroke={color}
            strokeWidth={2.5}
            dot={{ r: 4, fill: color }}
            activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};
