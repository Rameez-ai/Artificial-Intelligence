import client from './client';

export const predictLoan    = (data) => client.post('/api/loan/predict',     data);
export const getLoanHistory = ()     => client.get('/api/loan/history');
export const getSuggestions = ()     => client.get('/api/loan/suggestions');
