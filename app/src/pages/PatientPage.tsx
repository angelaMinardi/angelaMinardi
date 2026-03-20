import React from 'react';
import { PatientDashboard } from '../components/patient/Dashboard';
import { useGaitData } from '../hooks/useGaitData';

export const PatientPage: React.FC = () => {
  useGaitData();
  return <PatientDashboard />;
};
