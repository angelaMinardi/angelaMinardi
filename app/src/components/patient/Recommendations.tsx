import React from 'react';

interface Props {
  category: 'low' | 'moderate' | 'high';
}

const RECS: Record<string, { title: string; items: string[] }> = {
  low: {
    title: 'Keep It Up',
    items: [
      'Continue your daily walking routine',
      'Practice balance exercises 3x per week (e.g., single-leg stands)',
      'Stay hydrated and maintain a balanced diet',
      'Ensure your footwear fits properly and has non-slip soles',
    ],
  },
  moderate: {
    title: 'Recommended Actions',
    items: [
      'Increase balance training to daily sessions (heel-to-toe walking, tandem stance)',
      'Review your medications with your doctor for dizziness side effects',
      'Install grab bars in bathroom and handrails on stairs',
      'Use a walking aid on uneven surfaces or when fatigued',
      'Have your vision checked if overdue',
      'Consider a physical therapy evaluation',
    ],
  },
  high: {
    title: 'Priority Actions',
    items: [
      'Schedule an appointment with your healthcare provider',
      'Use a walking aid (cane or walker) until risk decreases',
      'Remove tripping hazards from your home (loose rugs, cords, clutter)',
      'Ensure adequate lighting in all walkways and stairwells',
      'Ask your pharmacist to review all medications for fall risk',
      'Consider a home safety assessment by an occupational therapist',
      'Wear your insole daily so we can monitor your progress',
    ],
  },
};

export const Recommendations: React.FC<Props> = ({ category }) => {
  const { title, items } = RECS[category];
  return (
    <div className="bg-white rounded-xl shadow-sm border p-5">
      <h3 className="text-sm font-medium text-gray-500 mb-3">{title}</h3>
      <ul className="space-y-2">
        {items.map((item, i) => (
          <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
            <span className="text-indigo-500 mt-0.5 flex-shrink-0">&bull;</span>
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
};
