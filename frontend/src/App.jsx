import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Login from './features/auth/Login';
import InputWizard from './features/dashboard/InputWizard';
import ResultsDashboard from './features/simulators/ResultsDashboard';
import VendorMarketplace from './features/marketplace/VendorMarketplace';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Set the Input Wizard as the home page. 
            Our security code in InputWizard will automatically kick them to /login if they don't have a token. */}
        <Route path="/" element={<InputWizard />} />
        <Route path="/login" element={<Login />} />
        <Route path="/results" element={<ResultsDashboard />} />
        <Route path="/marketplace" element={<VendorMarketplace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;