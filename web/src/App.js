import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Home         from './Home';
import DetailsPage  from './DetailsPage';
import SummaryPage  from './SummaryPage';  // ← new
import DetailedSummaryPage from './DetailedSummaryPage';
import './index.css';

export default function App() {
  return (
    <Routes>
      <Route path="/"                         element={<Home />} />
      <Route path="/details-page/:policyId"  element={<DetailsPage />} />
      <Route path="/summary"                  element={<SummaryPage />} />
      <Route path="/summary/:datasetName" element={<DetailedSummaryPage />} />
      {/* You can add a catch-all 404 route if you like */}
    </Routes>
  );
}
