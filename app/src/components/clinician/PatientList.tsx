import React from 'react';
import type { Patient } from '../../types';

interface Props {
  patients: Patient[];
  selectedId: string | null;
  onSelect: (id: string) => void;
}

function latestRisk(p: Patient) {
  return p.assessments[p.assessments.length - 1] ?? null;
}

function trendArrow(p: Patient): string {
  const a = p.assessments;
  if (a.length < 2) return '--';
  const recent = a.slice(-3).reduce((s, x) => s + x.score, 0) / Math.min(a.length, 3);
  const prior =
    a.slice(-6, -3).reduce((s, x) => s + x.score, 0) /
    Math.min(Math.max(a.length - 3, 1), 3);
  if (recent > prior + 0.05) return '\u2191';
  if (recent < prior - 0.05) return '\u2193';
  return '\u2192';
}

const RISK_BADGE: Record<string, string> = {
  low: 'bg-green-100 text-green-700',
  moderate: 'bg-amber-100 text-amber-700',
  high: 'bg-red-100 text-red-700',
};

export const PatientList: React.FC<Props> = ({ patients, selectedId, onSelect }) => {
  return (
    <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
      <div className="px-4 py-3 border-b bg-gray-50">
        <h3 className="text-sm font-semibold text-gray-700">Patients</h3>
      </div>
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-gray-500 text-xs uppercase border-b">
            <th className="px-4 py-2">Name</th>
            <th className="px-4 py-2">Age/Sex</th>
            <th className="px-4 py-2">Risk</th>
            <th className="px-4 py-2">Trend</th>
            <th className="px-4 py-2">Last Reading</th>
          </tr>
        </thead>
        <tbody>
          {patients.map((p) => {
            const risk = latestRisk(p);
            const isSelected = p.id === selectedId;
            return (
              <tr
                key={p.id}
                onClick={() => onSelect(p.id)}
                className={`cursor-pointer border-b hover:bg-indigo-50 transition ${
                  isSelected ? 'bg-indigo-50' : ''
                }`}
              >
                <td className="px-4 py-3 font-medium text-gray-800">{p.name}</td>
                <td className="px-4 py-3 text-gray-600">
                  {p.age}{p.sex}
                </td>
                <td className="px-4 py-3">
                  {risk && (
                    <span
                      className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                        RISK_BADGE[risk.category]
                      }`}
                    >
                      {Math.round(risk.score * 100)}
                    </span>
                  )}
                </td>
                <td className="px-4 py-3 text-lg">{trendArrow(p)}</td>
                <td className="px-4 py-3 text-gray-500 text-xs">
                  {p.lastReading
                    ? new Date(p.lastReading).toLocaleDateString()
                    : '--'}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};
