// web/src/Home.js

import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import './index.css';

export default function Home() {
  const [policyId, setPolicyId] = useState('');
  const navigate = useNavigate();

  const onSearch = () => {
    if (policyId.trim()) {
      navigate(`/details-page/${policyId.trim()}`);
    }
  };

  return (
    <div className="app">
      <div className="header centered-header">
        {/* Left: NSG Logo */}
        <Link to="/" className="logo-link header-logo">
          <img src="/logo.png" alt="NSG Logo" className="logo" />
        </Link>

        {/* Center: Title */}
        <h1 className="header-title">Car Insurance Claim</h1>

        {/* Right: View Summary button */}
        <Link to="/summary" className="oval-btn header-summary-btn">
          View Summary
        </Link>
      </div>

      <div className="form-container centered">
        <input
          type="text"
          placeholder="🆔 Enter Policy ID"
          value={policyId}
          onChange={e => setPolicyId(e.target.value)}
          onKeyDown={e => {
            if (e.key === 'Enter') {
              onSearch();
            }
          }}
          className="home-input"
        />
        <button
          className="home-btn"
          onClick={onSearch}
        >
          Search
        </button>
      </div>
    </div>
  );
}
