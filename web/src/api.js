import axios from 'axios';

const BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const client = axios.create({ baseURL: BASE });

// default summary.txt
export function fetchSummary() {
  return client.get('/summary', { responseType: 'text' })
               .then(r => r.data);
}

// specific uploaded summary
export function fetchUploadedSummary(datasetName) {
  return client.get(`/summary/${datasetName}`, { responseType: 'text' })
               .then(r => r.data);
}

// record lookup
export function getRecord(policyId) {
  return client.get(`/record/${policyId}`).then(r => r.data);
}

// the one you already had
export function predict(params) {
  return client.post('/predict', params).then(r => r.data);
}

// ALIAS predict → predictManual for backward compatibility
export const predictManual = predict;
