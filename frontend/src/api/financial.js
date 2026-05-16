import client from './client';

export const getDashboard   = ()     => client.get('/api/financial/dashboard');
export const getHealthScore = (data) => client.post('/api/financial/health-score', data);
export const getRiskAnalysis= (data) => client.post('/api/financial/risk-analysis', data);
export const simulate       = (data) => client.post('/api/financial/simulate', data);
