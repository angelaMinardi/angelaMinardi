import React from 'react';
import { useGaitStore } from '../../store/gaitStore';
import { PatientList } from './PatientList';
import { PressureHeatmap } from './PressureHeatmap';
import { GaitAnalytics } from './GaitAnalytics';
import { TemporalAnalysis } from './TemporalAnalysis';
import { ReportExport } from './ReportExport';
import { RiskGauge } from '../common/RiskGauge';

export const ClinicianDashboard: React.FC = () => {
  const { patients, selectedPatientId, selectPatient, latestFeatures } =
    useGaitStore();

  const selectedPatient = patients.find((p) => p.id === selectedPatientId);
  const latestRisk = selectedPatient?.assessments[selectedPatient.assessments.length - 1];

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-800">Clinical Dashboard</h1>
        {selectedPatient && latestFeatures && (
          <ReportExport patient={selectedPatient} features={latestFeatures} />
        )}
      </div>

      {/* Patient list */}
      <PatientList
        patients={patients}
        selectedId={selectedPatientId}
        onSelect={selectPatient}
      />

      {/* Patient detail */}
      {selectedPatient ? (
        <div className="space-y-6">
          <div className="flex items-center gap-3">
            <h2 className="text-lg font-semibold text-gray-700">
              {selectedPatient.name}
            </h2>
            <span className="text-sm text-gray-500">
              {selectedPatient.age}{selectedPatient.sex}
            </span>
          </div>

          {/* Risk + Pressure side by side */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white rounded-xl shadow-sm border p-6 flex flex-col items-center justify-center">
              {latestRisk && <RiskGauge assessment={latestRisk} size={180} />}
              {latestRisk && (
                <div className="mt-3 text-xs text-gray-500 text-center">
                  <p className="font-medium mb-1">Top Factors:</p>
                  {latestRisk.topFactors.map((f, i) => (
                    <p key={i}>{f}</p>
                  ))}
                </div>
              )}
            </div>
            <PressureHeatmap />
            {latestFeatures && (
              <div className="bg-white rounded-xl shadow-sm border p-4">
                <h3 className="text-sm font-medium text-gray-500 mb-3">Key Metrics</h3>
                <div className="space-y-3">
                  <MetricRow label="Walking Speed" value={`${latestFeatures.walking_speed.toFixed(2)} m/s`} norm="1.0-1.4" />
                  <MetricRow label="Cadence" value={`${latestFeatures.cadence.toFixed(0)} steps/min`} norm="100-120" />
                  <MetricRow label="Stride Variability" value={`${latestFeatures.stride_time_cv.toFixed(1)}% CV`} norm="<4%" />
                  <MetricRow label="ML Sway" value={`${latestFeatures.sway_rms.toFixed(3)} g RMS`} norm="<0.15" />
                  <MetricRow label="Symmetry Index" value={latestFeatures.pressure_symmetry_index.toFixed(2)} norm=">0.90" />
                  <MetricRow label="Foot Temp" value={`${latestFeatures.foot_temperature.toFixed(1)} C`} norm="28-32" />
                  <MetricRow label="Steps Today" value={latestFeatures.step_count.toLocaleString()} norm=">4000" />
                </div>
              </div>
            )}
          </div>

          {/* Gait analytics */}
          {latestFeatures && <GaitAnalytics features={latestFeatures} />}

          {/* Temporal analysis */}
          <TemporalAnalysis patient={selectedPatient} />
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm border p-12 text-center text-gray-400">
          Select a patient to view detailed gait analysis
        </div>
      )}
    </div>
  );
};

const MetricRow: React.FC<{ label: string; value: string; norm: string }> = ({
  label,
  value,
  norm,
}) => (
  <div className="flex justify-between text-sm">
    <span className="text-gray-600">{label}</span>
    <div className="text-right">
      <span className="font-medium text-gray-800">{value}</span>
      <span className="text-xs text-gray-400 ml-1">({norm})</span>
    </div>
  </div>
);
