import React from 'react';
import type { RiskAssessment } from '../../types';

interface Props {
  assessment: RiskAssessment;
}

const ICONS = { low: 'check', moderate: 'warning', high: 'alert' };

const MESSAGES: Record<string, string[]> = {
  low: ['Your gait looks stable today. Keep up the good work!'],
  moderate: [
    'Your fall risk is slightly elevated today.',
    'Consider using a walking aid if available.',
    'Take extra care on stairs and uneven surfaces.',
  ],
  high: [
    'Your fall risk is elevated. Please take precautions.',
    'Use a walking aid and avoid uneven terrain.',
    'Consider contacting your healthcare provider.',
  ],
};

const COLORS = {
  low: 'bg-green-50 border-green-200 text-green-800',
  moderate: 'bg-amber-50 border-amber-200 text-amber-800',
  high: 'bg-red-50 border-red-200 text-red-800',
};

const ICON_BG = {
  low: 'bg-green-100 text-green-600',
  moderate: 'bg-amber-100 text-amber-600',
  high: 'bg-red-100 text-red-600',
};

export const AlertBanner: React.FC<Props> = ({ assessment }) => {
  const { category, topFactors } = assessment;
  const messages = MESSAGES[category];
  const icon = ICONS[category];

  return (
    <div className={`rounded-xl border p-4 ${COLORS[category]}`}>
      <div className="flex items-start gap-3">
        <div className={`p-2 rounded-lg ${ICON_BG[category]} flex-shrink-0`}>
          <span className="text-lg">
            {icon === 'check' && '\u2713'}
            {icon === 'warning' && '\u26A0'}
            {icon === 'alert' && '\u26D4'}
          </span>
        </div>
        <div>
          <p className="font-semibold text-sm">{messages[0]}</p>
          {messages.slice(1).map((msg, i) => (
            <p key={i} className="text-sm mt-1 opacity-80">
              {msg}
            </p>
          ))}
          {topFactors.length > 0 && category !== 'low' && (
            <div className="mt-2 text-xs opacity-70">
              <span className="font-medium">Contributing factors: </span>
              {topFactors.join(', ')}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
