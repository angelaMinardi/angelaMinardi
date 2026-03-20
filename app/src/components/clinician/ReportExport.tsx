import React, { useCallback } from 'react';
import jsPDF from 'jspdf';
import type { Patient, GaitFeatures } from '../../types';

interface Props {
  patient: Patient;
  features: GaitFeatures;
}

export const ReportExport: React.FC<Props> = ({ patient, features }) => {
  const generatePDF = useCallback(() => {
    const doc = new jsPDF();
    const latestRisk = patient.assessments[patient.assessments.length - 1];
    let y = 20;

    // Header
    doc.setFontSize(18);
    doc.setFont('helvetica', 'bold');
    doc.text('Fall Risk Assessment Report', 20, y);
    y += 10;
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    doc.text(`Generated: ${new Date().toLocaleString()}`, 20, y);
    y += 15;

    // Patient info
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.text('Patient Information', 20, y);
    y += 8;
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    const info = [
      `Name: ${patient.name}`,
      `Age: ${patient.age} | Sex: ${patient.sex}`,
      `Assessment Date: ${latestRisk ? new Date(latestRisk.timestamp).toLocaleDateString() : 'N/A'}`,
    ];
    info.forEach((line) => {
      doc.text(line, 25, y);
      y += 6;
    });
    y += 5;

    // Risk score
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.text('Fall Risk Assessment', 20, y);
    y += 8;
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    if (latestRisk) {
      doc.text(`Risk Score: ${Math.round(latestRisk.score * 100)} / 100`, 25, y);
      y += 6;
      doc.text(`Category: ${latestRisk.category.toUpperCase()}`, 25, y);
      y += 6;
      doc.text(`Contributing Factors: ${latestRisk.topFactors.join(', ')}`, 25, y);
      y += 10;
    }

    // Gait parameters table
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.text('Gait Parameters', 20, y);
    y += 8;
    doc.setFontSize(9);
    doc.setFont('helvetica', 'normal');

    const params: [string, string, string][] = [
      ['Cadence', `${features.cadence.toFixed(1)} steps/min`, '100-120'],
      ['Stride Length', `${features.stride_length_mean.toFixed(2)} m`, '1.2-1.5'],
      ['Walking Speed', `${features.walking_speed.toFixed(2)} m/s`, '1.0-1.4'],
      ['Stance Phase', `${features.stance_phase_pct.toFixed(1)}%`, '58-62%'],
      ['Double Support', `${features.double_support_pct.toFixed(1)}%`, '10-15%'],
      ['Stride Time CV', `${features.stride_time_cv.toFixed(1)}%`, '<4%'],
      ['M-L Sway (RMS)', `${features.sway_rms.toFixed(3)} g`, '<0.15'],
      ['Pressure Symmetry', `${features.pressure_symmetry_index.toFixed(2)}`, '>0.90'],
      ['Foot Temperature', `${features.foot_temperature.toFixed(1)} C`, '28-32'],
      ['Step Count', `${features.step_count}`, '>4000/day'],
    ];

    // Table header
    doc.setFont('helvetica', 'bold');
    doc.text('Parameter', 25, y);
    doc.text('Value', 90, y);
    doc.text('Normal Range', 140, y);
    y += 2;
    doc.line(25, y, 185, y);
    y += 5;
    doc.setFont('helvetica', 'normal');

    params.forEach(([name, value, norm]) => {
      doc.text(name, 25, y);
      doc.text(value, 90, y);
      doc.text(norm, 140, y);
      y += 5;
    });
    y += 5;

    // Risk history
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.text('30-Day Risk History', 20, y);
    y += 8;
    doc.setFontSize(9);
    doc.setFont('helvetica', 'normal');

    const recent = patient.assessments.slice(-10);
    recent.forEach((a) => {
      doc.text(
        `${new Date(a.timestamp).toLocaleDateString()}: Score ${Math.round(a.score * 100)} (${a.category})`,
        25,
        y
      );
      y += 5;
    });

    // Footer
    y = 280;
    doc.setFontSize(8);
    doc.setTextColor(128);
    doc.text(
      'Smart Insole Fall Prevention System - For clinical use only. This report does not constitute medical advice.',
      20,
      y
    );

    doc.save(`fall-risk-report-${patient.name.replace(/\s+/g, '-')}.pdf`);
  }, [patient, features]);

  return (
    <button
      onClick={generatePDF}
      className="px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition flex items-center gap-2"
    >
      <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
        <path d="M4 1h8a1 1 0 011 1v12a1 1 0 01-1 1H4a1 1 0 01-1-1V2a1 1 0 011-1zm1 3v2h6V4H5zm0 4v1h6V8H5zm0 3v1h4v-1H5z" />
      </svg>
      Export PDF Report
    </button>
  );
};
