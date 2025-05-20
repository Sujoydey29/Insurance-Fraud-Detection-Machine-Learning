import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { fetchUploadedSummary } from './api';
import {
  BarChart, Bar, XAxis,
  PieChart, Pie, Cell, Legend,
  LineChart, Line, CartesianGrid,
  XAxis as LineX, Tooltip as RechartsTooltip,
  ResponsiveContainer
} from 'recharts';
import './index.css';

export default function DetailedSummaryPage() {
  const { datasetName } = useParams();
  const [metrics, setMetrics] = useState(null);

  const parseSummary = txt => {
    const lines = txt.split('\n').map(l => l.trim());
    const find = label => {
      const row = lines.find(r => r.startsWith(label));
      if (!row) return 0;
      const raw = row.split(':')[1].trim();
      return label.includes('Accuracy')
        ? parseFloat(raw.replace('%',''))
        : parseInt(raw.replace(/,/g,''),10);
    };
    return {
      total:            find('Total Records'),
      actualGenuine:    find('Actual Genuine Claims'),
      predictedGenuine: find('Predicted Genuine Claims'),
      actualFraud:      find('Actual Fraud Claims'),
      predictedFraud:   find('Predicted Fraud Claims'),
      correct:          find('Correctly Predicted'),
      incorrect:        find('Incorrectly Predicted'),
      accuracy:         find('Accuracy of the Model is'),
    };
  };

  useEffect(() => {
    fetchUploadedSummary(datasetName)
      .then(txt => setMetrics(parseSummary(txt)))
      .catch(console.error);
  }, [datasetName]);

  if (!metrics) {
    return (
      <div className="app">
        <div className="header">
          <h1>Loading {datasetName}…</h1>
          <Link to="/summary">← Back</Link>
        </div>
        <div className="form-container centered">
          <div className="loading">Loading…</div>
        </div>
      </div>
    );
  }

  const {
    total,
    actualGenuine,
    predictedGenuine,
    actualFraud,
    predictedFraud,
    correct,
    incorrect,
    accuracy
  } = metrics;

  const fraudRate = total ? ((predictedFraud / total) * 100).toFixed(0) + '%' : '0%';

  const barData = [
    { name: 'Act Gen',   value: actualGenuine },
    { name: 'Pred Gen',   value: predictedGenuine },
    { name: 'Act Fraud',   value: actualFraud },
    { name: 'Pred Fraud',   value: predictedFraud },
    { name: 'Correctly P', value: correct },
    { name: 'Incorrectly P',  value: incorrect },
  ];

  const pie1 = [
    { name: 'Genuine', value: predictedGenuine, fill: '#00C49F' },
    { name: 'Fraud',   value: predictedFraud,    fill: '#FF8042' },
  ];
  const pie2 = [
    { name: 'Correct',   value: correct,   fill: '#4e54c8' },
    { name: 'Incorrect', value: incorrect, fill: '#e74c3c' },
  ];

  

  return (
    <div className="app">
      <div className="header">
        <h1>Summary for {datasetName}</h1>
        <Link to="/summary" className="logo-link">← Upload Another</Link>
      </div>

      <div className="form-container">

        {/* KPI ROW */}
        <div className="kpi-row">
          <div className="kpi-card">
            <div className="kpi-value">{total.toLocaleString()}</div>
            <div className="kpi-label">Total Claims</div>
          </div>
          <div className="kpi-card">
            <div className="kpi-value">{predictedGenuine.toLocaleString()}</div>
            <div className="kpi-label">Genuine Claims</div>
          </div>
          <div className="kpi-card">
            <div className="kpi-value">{predictedFraud.toLocaleString()}</div>
            <div className="kpi-label">Fraudulent Claims</div>
          </div>
          <div className="kpi-card">
            <div className="kpi-value">{fraudRate}</div>
            <div className="kpi-label">Fraud Rate</div>
          </div>
        </div>

        {/* ACCURACY CARD */}
        <div className="summary-card floating">
          <div className="kpi-value">{accuracy.toFixed(2)}%</div>
          <div className="kpi-label">Model Accuracy</div>
        </div>

        {/* PILL BARS */}
        <div className="charts-row">
          <div className="chart-card full-width small-card">
            <h3>Statistics</h3>
            <ResponsiveContainer width="100%" height={180}>
              <BarChart data={barData} barSize={24} barCategoryGap="20%">
                <XAxis dataKey="name" axisLine={false} tickLine={false} />
                <defs>
                  <linearGradient id="gradBar" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#4e54c8" stopOpacity={0.9}/>
                    <stop offset="100%" stopColor="#8f94fb" stopOpacity={0.9}/>
                  </linearGradient>
                </defs>
                <Bar dataKey="value" fill="url(#gradBar)" radius={[6,6,0,0]} />
                <RechartsTooltip formatter={(val,name)=>[val.toLocaleString(),name]} cursor={{ fill:'rgba(0,0,0,0.1)' }} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div>
          <br></br>
        </div>

        {/* PIE CHARTS */}
        <div className="charts-row">
          <div className="chart-card">
            <h2>Claims</h2>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie data={pie1} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} paddingAngle={4}>
                  {pie1.map((e,i)=><Cell key={i} fill={e.fill}/>)}
                </Pie>
                <Legend verticalAlign="bottom" iconSize={8}/>
                <RechartsTooltip formatter={(val,name)=>{
                  const tot=pie1.reduce((s,e)=>s+e.value,0);
                  return [`${((val/tot)*100).toFixed(1)}%`,name];
                }}/>
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="chart-card">
            <h2>Model Prediction</h2>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie data={pie2} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} paddingAngle={4}>
                  {pie2.map((e,i)=><Cell key={i} fill={e.fill}/>)}
                </Pie>
                <Legend verticalAlign="bottom" iconSize={8}/>
                <RechartsTooltip formatter={(val,name)=>{
                  const tot=pie2.reduce((s,e)=>s+e.value,0);
                  return [`${((val/tot)*100).toFixed(1)}%`,name];
                }}/>
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        
        
      </div>
      <div
        className="fab"
        title="Back to Top"
        onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
      >
        ↑
      </div>
    </div>
  );
}
