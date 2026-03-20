import React, { useMemo } from 'react';
import { generateMockPressureData } from '../../store/mockData';

interface Props {
  pressureData?: number[];
  width?: number;
  height?: number;
}

const ZONE_POSITIONS = [
  { name: 'Heel Center', x: 0.50, y: 0.85, r: 0.09 },
  { name: 'Heel Medial', x: 0.35, y: 0.80, r: 0.07 },
  { name: 'Heel Lateral', x: 0.65, y: 0.80, r: 0.07 },
  { name: 'Midfoot Arch', x: 0.40, y: 0.55, r: 0.06 },
  { name: '1st Metatarsal', x: 0.30, y: 0.30, r: 0.08 },
  { name: '3rd Metatarsal', x: 0.50, y: 0.25, r: 0.07 },
  { name: '5th Metatarsal', x: 0.70, y: 0.30, r: 0.07 },
  { name: 'Big Toe', x: 0.30, y: 0.10, r: 0.06 },
];

function pressureColor(value: number, max: number): string {
  const ratio = Math.min(value / max, 1);
  if (ratio < 0.25) return `rgba(59, 130, 246, ${0.3 + ratio * 2})`;
  if (ratio < 0.5) return `rgba(234, 179, 8, ${0.4 + ratio})`;
  if (ratio < 0.75) return `rgba(249, 115, 22, ${0.5 + ratio * 0.5})`;
  return `rgba(239, 68, 68, ${0.6 + ratio * 0.4})`;
}

export const PressureHeatmap: React.FC<Props> = ({
  pressureData,
  width = 220,
  height = 400,
}) => {
  const data = useMemo(() => pressureData ?? generateMockPressureData(), [pressureData]);
  const maxPressure = Math.max(...data, 1);

  return (
    <div className="bg-white rounded-xl shadow-sm border p-4">
      <h3 className="text-sm font-medium text-gray-500 mb-3">Plantar Pressure Map</h3>
      <div className="flex justify-center">
        <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`}>
          {/* Foot outline */}
          <path
            d={`
              M ${width * 0.5} ${height * 0.02}
              C ${width * 0.15} ${height * 0.05} ${width * 0.10} ${height * 0.20} ${width * 0.15} ${height * 0.35}
              C ${width * 0.20} ${height * 0.50} ${width * 0.18} ${height * 0.60} ${width * 0.20} ${height * 0.70}
              C ${width * 0.22} ${height * 0.80} ${width * 0.25} ${height * 0.90} ${width * 0.30} ${height * 0.95}
              C ${width * 0.40} ${height * 0.98} ${width * 0.60} ${height * 0.98} ${width * 0.70} ${height * 0.95}
              C ${width * 0.75} ${height * 0.90} ${width * 0.78} ${height * 0.80} ${width * 0.80} ${height * 0.70}
              C ${width * 0.82} ${height * 0.60} ${width * 0.80} ${height * 0.50} ${width * 0.85} ${height * 0.35}
              C ${width * 0.90} ${height * 0.20} ${width * 0.85} ${height * 0.05} ${width * 0.5} ${height * 0.02}
              Z
            `}
            fill="#f9fafb"
            stroke="#d1d5db"
            strokeWidth="1.5"
          />
          {/* Pressure zones */}
          {ZONE_POSITIONS.map((zone, i) => {
            const cx = zone.x * width;
            const cy = zone.y * height;
            const r = zone.r * width;
            const value = data[i] ?? 0;
            return (
              <g key={zone.name}>
                <circle
                  cx={cx}
                  cy={cy}
                  r={r}
                  fill={pressureColor(value, maxPressure)}
                  stroke="rgba(0,0,0,0.1)"
                  strokeWidth="0.5"
                />
                <text
                  x={cx}
                  y={cy + 1}
                  textAnchor="middle"
                  dominantBaseline="central"
                  fontSize="9"
                  fill="#1f2937"
                  fontWeight="600"
                >
                  {Math.round(value)}
                </text>
              </g>
            );
          })}
        </svg>
      </div>
      {/* Legend */}
      <div className="flex items-center justify-center gap-2 mt-3 text-xs text-gray-500">
        <span>Low</span>
        <div className="flex">
          {['#3b82f6', '#eab308', '#f97316', '#ef4444'].map((c) => (
            <div key={c} className="w-6 h-3" style={{ backgroundColor: c }} />
          ))}
        </div>
        <span>High</span>
        <span className="ml-2 text-gray-400">(units: arbitrary)</span>
      </div>
    </div>
  );
};
