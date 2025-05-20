import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { getRecord, predictManual } from './api';
import Modal from './Modal';
import './index.css';

export default function DetailsPage() {
  const { policyId } = useParams();
  const navigate = useNavigate();
  const [rec, setRec] = useState(null);
  const [modalData, setModal] = useState(null);
  const [incidentError, setIncidentError] = useState('');
  const [incidentTouched, setIncidentTouched] = useState(false);

  // Fetch logic
  const fetchData = () => {
    getRecord(policyId)
      .then(record => {
        if (!record) throw new Error();
        setRec({
          policy_status: record.policy_status,
          driver_age: record.driver_age,
          model: record.model,
          fuel_type: record.fuel_type,
          transmission_type: record.transmission_type,
          no_previous_claims: record.no_previous_claims,
          time_of_incident: record.time_of_incident,
          fir_filed: record.fir_filed,
          license: record.license,
          drunk_driving: record.drunk_driving,
        });
      })
      .catch(() => {
        setModal({
          title: <span style={{ color: 'red' }}>Policy ID Not Found!</span>,
          content: <p>No record found for Policy ID: <strong>{policyId}</strong></p>
        });
      });
  };

  useEffect(fetchData, [policyId]);

  // Enter-key listener
  useEffect(() => {
    const handleKeyDown = e => {
      if (e.key === 'Enter' && !modalData) {
        e.preventDefault();
        onPredict();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [rec, modalData]);

  // Show error modal before record loads
  if (modalData && !rec) {
    return (
      <div className="app">
        <Modal
          title={modalData.title}
          onClose={() => {
            setModal(null);
            navigate('/');
          }}
        >
          {modalData.content}
        </Modal>
      </div>
    );
  }

  // Loading state
  if (!rec) {
    return (
      <div className="app">
        <div className="loading">Loading…</div>
      </div>
    );
  }

  // Field updater
  const updateField = (field, value) => {
    if (field === 'time_of_incident') setIncidentError('');
    setRec(prev => ({ ...prev, [field]: value }));
  };

  // IST utilities
  const getCurrentIST = () => {
    const now = new Date();
    const opts = { timeZone: 'Asia/Kolkata', hour12: true, year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' };
    const parts = new Intl.DateTimeFormat('en-GB', opts).formatToParts(now);
    const map = Object.fromEntries(parts.map(p => [p.type, p.value]));
    return `${map.year}-${map.month}-${map.day} ${map.hour}:${map.minute} ${map.dayPeriod} IST`;
  };

  const parseIST = str => {
    if (!str) return null;
    try {
      const [datePart, timePart, period] = str.replace(' IST', '').split(' ');
      let [year, month, day] = datePart.split('-').map(Number);
      let [hour, minute] = timePart.split(':').map(Number);
      const up = period.toUpperCase();
      if (up === 'PM' && hour < 12) hour += 12;
      if (up === 'AM' && hour === 12) hour = 0;
      return new Date(year, month - 1, day, hour, minute);
    } catch {
      return null;
    }
  };

  const isFutureTime = inputStr => {
    const inputDate = parseIST(inputStr);
    if (!inputDate) return { valid: false, message: 'Invalid format. Use: YYYY-MM-DD HH:MM AM/PM IST'};
    const nowDate = parseIST(getCurrentIST());
    return inputDate > nowDate
      ? { valid: false, message: 'Time entered is in the future.' }
      : { valid: true, message: 'Valid input.' };
  };

  // Submit handler
  const onPredict = () => {
    if (!incidentTouched) { setIncidentError('Please fill all the fields'); return; }
    if (!rec.time_of_incident) { setIncidentError('Please enter incident time'); return; }
    const incidentDate = parseIST(rec.time_of_incident);
    if (!incidentDate) { setIncidentError('Please enter incident time in correct format: YYYY-MM-DD HH:MM AM/PM IST'); return; }
    const { valid, message } = isFutureTime(rec.time_of_incident);
    if (!valid) { setIncidentError(message); return; }
    setIncidentError('');

    const payload = {
      policy_status: rec.policy_status,
      license: rec.license,
      driver_age: Number(rec.driver_age),
      drunk_driving: rec.drunk_driving,
      fir_filed: rec.fir_filed,
      no_previous_claims: Number(rec.no_previous_claims),
      time_of_incident: rec.time_of_incident,
      time_of_claim: getCurrentIST(),
    };

    predictManual(payload)
      .then(res => {
        const genuine = res.genuine_probability * 100;
        const fraud = res.fraud_probability * 100;
        let title = 'Fraud Claim', titleColor = 'red';
        if (genuine >= fraud && genuine >= 80) { title = 'Genuine Claim'; titleColor = 'green'; }
        else if (genuine >= 50) { title = 'Need Further Investigation'; titleColor = 'orange'; }
        
        setModal({
          title: <span style={{color: titleColor}}>{title}</span>,
          content: <>
            <p style={{color: 'green'}}>🟢 Genuinity: {genuine.toFixed(1)}%</p>
            <p style={{color: 'red', marginTop: '0.5rem'}}>🔴 Chance of Fraud: {fraud.toFixed(1)}%</p>
          </>
        });
      })
      .catch(err => {
        setModal({ title: <span style={{color:'red'}}>Error</span>, content: <p>{err.message || 'Wrong input'}</p> });
      });
  };

  // Render
  return (
    <div className="app">
      <div className="header">
        <Link to="/" className="logo-link"><img src="/logo.png" alt="NSG Logo" className="logo"/></Link>
        <h1>Policy Details: {policyId}</h1>
        <Link to="/summary" className="oval-btn">View Summary</Link>
      </div>
      <div className="form-container">
        <h2>Vehicle & Driver Info</h2>
        <table className="data-table"><tbody>
          <tr><td><strong>Policy Status</strong></td><td><span className="readonly-field">{rec.policy_status}</span></td>
              <td><strong>Driver Age</strong></td><td><span className="readonly-field">{rec.driver_age}</span></td></tr>
          <tr><td><strong>Model</strong></td><td><span className="readonly-field">{rec.model}</span></td>
              <td><strong>Fuel Type</strong></td><td><span className="readonly-field">{rec.fuel_type}</span></td></tr>
          <tr><td><strong>Transmission</strong></td><td><span className="readonly-field">{rec.transmission_type}</span></td>
              <td><strong>Previous Claims</strong></td><td><input type="number" min="0" value={rec.no_previous_claims} onChange={e=>updateField('no_previous_claims',e.target.value)}/></td></tr>
        </tbody></table>
        <h2>Claim Parameters</h2>
        <div className="claim-params">
          <div className="field-inline" style={{flexDirection:'column',alignItems:'flex-start'}}>
            <label>⏱️ Incident</label>
            <input type="text" placeholder="YYYY-MM-DD HH:MM AM/PM IST" onChange={e=>{updateField('time_of_incident',e.target.value);setIncidentTouched(true);}} />
            {incidentError && <div style={{color:'red',fontSize:'0.85rem',marginTop:'0.25rem'}}>{incidentError}</div>}
          </div>
          <div className="field-inline"><label>⏱️ Claim (Now)</label><input type="text" value={getCurrentIST()} readOnly/></div>
          <div className="field-inline"><label>📄 FIR Filed?</label><select value={rec.fir_filed} onChange={e=>updateField('fir_filed',e.target.value)}><option>Yes</option><option>No</option></select></div>
          <div className="field-inline"><label>🪪 License</label><select value={rec.license} onChange={e=>updateField('license',e.target.value)}><option>Yes</option><option>No</option></select></div>
          <div className="field-inline"><label>🍺 Drunk Driving</label><select value={rec.drunk_driving} onChange={e=>updateField('drunk_driving',e.target.value)}><option>No</option><option>Yes</option></select></div>
        </div>
        <button className="oval-btn" onClick={onPredict}>Submit</button>
      </div>
      <div className="fab" title="Back to Top" onClick={()=>window.scrollTo({top:0,behavior:'smooth'})}>↑</div>
      {modalData && rec && <Modal title={modalData.title} onClose={()=>setModal(null)}>{modalData.content}</Modal>}
    </div>
  );
}
