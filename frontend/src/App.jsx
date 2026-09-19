import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './features/auth/Login.jsx';
import InputWizard from './features/dashboard/InputWizard.jsx';
import ResultsDashboard from './features/simulators/ResultsDashboard.jsx';
import VendorMarketplace from './features/marketplace/VendorMarketplace';


function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="/login" element={<Login />} />
        <Route path="/wizard" element={<InputWizard />} />
        <Route path="/results" element={<ResultsDashboard />} />
        <Route path="/marketplace" element={<VendorMarketplace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;