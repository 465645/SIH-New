import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Login from './features/auth/Login';
import InputWizard from './features/dashboard/InputWizard';
import ResultsDashboard from './features/simulators/ResultsDashboard';
import VendorMarketplace from './features/marketplace/VendorMarketplace';
import OrderBoard from './features/marketplace/OrderBoard';
import ComplianceStudio from './features/compliance/ComplianceStudio';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Set the Input Wizard as the home page. 
            Our security code in InputWizard will automatically kick them to /login if they don't have a token. */}
        <Route path="/" element={<InputWizard />} />
        {/* Navbar and the results page both link to /wizard, so serve the same screen there. */}
        <Route path="/wizard" element={<InputWizard />} />
        <Route path="/login" element={<Login />} />
        <Route path="/results" element={<ResultsDashboard />} />
        <Route path="/marketplace" element={<VendorMarketplace />} />
        <Route path="/orders" element={<OrderBoard />} />
        <Route path="/compliance" element={<ComplianceStudio />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;