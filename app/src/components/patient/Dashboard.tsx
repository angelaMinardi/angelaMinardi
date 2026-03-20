import React from 'react';
import { useGaitStore } from '../../store/gaitStore';
import { RiskGauge } from '../common/RiskGauge';
import { TrendChart } from '../common/TrendChart';
import { AlertBanner } from '../common/AlertBanner';
import { DailyTrends } from './DailyTrends';
import { Recommendations } from './Recommendations';

export const PatientDashboard: React.FC = () => {
  const { currentRisk, dailyTrends, connected, deviceName, battery, latestFeatures } =
    useGaitStore();

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Connection status */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-800">My Fall Risk</h1>
        <div className="flex items-center gap-3">
          <div
            className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-sm ${
              connected
                ? 'bg-green-50 text-green-700 border border-green-200'
                : 'bg-gray-50 text-gray-500 border border-gray-200'
            }`}
          >
            <span className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500' : 'bg-gray-400'}`} />
            {connected ? `${deviceName} - ${battery}%` : 'Insole not connected'}
          </div>
        </div>
      </div>

      {/* Alert */}
      {currentRisk && <AlertBanner assessment={currentRisk} />}

      {/* Main gauge + stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-1 bg-white rounded-xl shadow-sm border p-6 flex justify-center">
          {currentRisk && <RiskGauge assessment={currentRisk} size={200} />}
        </div>
        <div className="md:col-span-2 grid grid-cols-2 gap-4">
          <StatCard
            label="Today's Steps"
            value={latestFeatures?.step_count.toLocaleString() ?? '--'}
            sub="steps"
          />
          <StatCard
            label="Walking Speed"
            value={latestFeatures?.walking_speed.toFixed(2) ?? '--'}
            sub="m/s"
          />
          <StatCard
            label="Cadence"
            value={latestFeatures?.cadence.toFixed(0) ?? '--'}
            sub="steps/min"
          />
          <StatCard
            label="Foot Temperature"
            value={latestFeatures?.foot_temperature.toFixed(1) ?? '--'}
            sub="C"
          />
        </div>
      </div>

      {/* 7-day trend */}
      <TrendChart data={dailyTrends} />

      {/* Daily details */}
      <DailyTrends trends={dailyTrends} />

      {/* Recommendations */}
      {currentRisk && <Recommendations category={currentRisk.category} />}
    </div>
  );
};

const StatCard: React.FC<{ label: string; value: string; sub: string }> = ({
  label,
  value,
  sub,
}) => (
  <div className="bg-white rounded-xl shadow-sm border p-4">
    <p className="text-xs text-gray-500 font-medium">{label}</p>
    <p className="text-2xl font-bold text-gray-800 mt-1">
      {value} <span className="text-sm font-normal text-gray-400">{sub}</span>
    </p>
  </div>
);
