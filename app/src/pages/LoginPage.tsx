import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useGaitStore } from '../store/gaitStore';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const setRole = useGaitStore((s) => s.setRole);

  const enter = (role: 'patient' | 'clinician') => {
    setRole(role);
    navigate(role === 'patient' ? '/patient' : '/clinician');
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-50 to-blue-100">
      <div className="bg-white rounded-2xl shadow-xl p-10 max-w-md w-full text-center">
        <div className="w-16 h-16 bg-indigo-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
          <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
            <path
              d="M16 4C10 4 8 10 8 16c0 4 1 8 4 10s4 2 4 2 1 0 4-2 4-6 4-10c0-6-2-12-8-12z"
              stroke="#6366f1"
              strokeWidth="2"
              fill="#e0e7ff"
            />
            <circle cx="12" cy="14" r="2" fill="#6366f1" />
            <circle cx="16" cy="20" r="2" fill="#6366f1" />
            <circle cx="20" cy="14" r="2" fill="#6366f1" />
          </svg>
        </div>
        <h1 className="text-2xl font-bold text-gray-800 mb-1">Smart Insole</h1>
        <p className="text-gray-500 text-sm mb-8">Fall Prevention System</p>

        <div className="space-y-3">
          <button
            onClick={() => enter('patient')}
            className="w-full py-3 px-4 bg-indigo-600 text-white rounded-xl font-medium hover:bg-indigo-700 transition"
          >
            I'm a Patient
          </button>
          <button
            onClick={() => enter('clinician')}
            className="w-full py-3 px-4 bg-white text-indigo-600 border-2 border-indigo-200 rounded-xl font-medium hover:bg-indigo-50 transition"
          >
            I'm a Healthcare Professional
          </button>
        </div>

        <p className="text-xs text-gray-400 mt-6">
          Connect your Smart Insole via Bluetooth to begin gait analysis
        </p>
      </div>
    </div>
  );
};
