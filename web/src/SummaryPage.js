import React, { useState, useRef, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import './index.css';

export default function SummaryPage() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  const handleFileChange = e => setFile(e.target.files[0]);

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    const datasetName = file.name.replace(/\.csv$/i, '');
    const form = new FormData();
    form.append('file', file);

    try {
      const res = await fetch('http://localhost:8000/summary/upload', {
        method: 'POST',
        body: form
      });
      if (!res.ok) {
        const errText = await res.text();
        throw new Error(errText);
      }
      navigate(`/summary/${encodeURIComponent(datasetName)}`);
    } catch (err) {
      console.error(err);
      alert('Upload failed:\n' + err.message);
    } finally {
      setUploading(false);
      setFile(null);
    }
  };

  useEffect(() => {
    const handleKeyDown = e => {
      if (e.key === 'Enter') {
        if (!file) {
          fileInputRef.current?.click(); // Open file dialog
        } else {
          handleUpload(); // Upload if file is selected
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [file]);

  return (
    <div className="app">
      {/* ── HEADER ───────────────────── */}
      <div className="header summary-header">
        <Link to="/" className="logo-link">
          <img src="/logo.png" alt="NSG Logo" className="logo" />
        </Link>
        <h1>Upload Data </h1>
        <Link to="/" className="logo-link">
          <img src="/logo.png" alt="NSG Logo" className="logo" />
        </Link>
      </div>

      {/* ── UPLOAD CARD ───────────────── */}
      <div className="form-container">
        <div className="upload-card glass-card">
          <input
            type="file"
            accept=".csv"
            onChange={handleFileChange}
            ref={fileInputRef}
            className="file-input"
          />
          <button
            onClick={handleUpload}
            disabled={!file || uploading}
            className="btn-primary"
          >
            {uploading ? 'Uploading…' : 'Upload & Analyze'}
          </button>
        </div>
      </div>
    </div>
  );
}
