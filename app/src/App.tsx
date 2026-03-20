import React from 'react';
import { Routes, Route, Navigate, Link, useLocation } from 'react-router-dom';
import { LoginPage } from './pages/LoginPage';
import { PatientPage } from './pages/PatientPage';
import { ClinicianPage } from './pages/ClinicianPage';
import { useGaitStore } from './store/gaitStore';
import { useBLE } from './hooks/useBLE';

const NavBar: React.FC = () => {
  const location = useLocation();
  const { role } = useGaitStore();
  const { connect, disconnect, scanning } = useBLE();
  const { connected, deviceName, battery } = useGaitStore();

  const isPatient = location.pathname.startsWith('/patient');
  const isClinician = location.pathname.startsWith('/clinician');

  return (
    <nav className="bg-white border-b px-6 py-3 flex items-center justify-between">
      <div className="flex items-center gap-6">
        <Link to="/" className="font-bold text-indigo-600 text-lg">
          SmartInsole
        </Link>
        <div className="flex gap-1">
          <Link
            to="/patient"
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition ${
              isPatient ? 'bg-indigo-100 text-indigo-700' : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Patient
          </Link>
          <Link
            to="/clinician"
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition ${
              isClinician ? 'bg-indigo-100 text-indigo-700' : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Clinician
          </Link>
        </div>
      </div>
      <div className="flex items-center gap-3">
        {connected && (
          <span className="text-xs text-gray-500">
            {deviceName} | {battery}%
          </span>
        )}
        <button
          onClick={connected ? disconnect : connect}
          disabled={scanning}
          className={`px-3 py-1.5 rounded-lg text-sm font-medium transition ${
            connected
              ? 'bg-red-50 text-red-600 hover:bg-red-100'
              : 'bg-indigo-50 text-indigo-600 hover:bg-indigo-100'
          } ${scanning ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          {scanning ? 'Scanning...' : connected ? 'Disconnect' : 'Connect Insole'}
        </button>
      </div>
    </nav>
  );
};

const App: React.FC = () => {
  return (
    <Routes>
      <Route path="/" element={<LoginPage />} />
      <Route
        path="/patient"
        element={
          <Layout>
            <PatientPage />
          </Layout>
        }
      />
      <Route
        path="/clinician"
        element={
          <Layout>
            <ClinicianPage />
          </Layout>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div className="min-h-screen bg-gray-50">
    <NavBar />
    <main className="p-6">{children}</main>
  </div>
);

export default App;
