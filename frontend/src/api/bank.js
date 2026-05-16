import client from './client';

export const listBanks   = ()      => client.get('/api/bank/list');
export const matchBanks  = (data)  => client.post('/api/bank/match', data);
export const policyChat  = (data)  => client.post('/api/bank/policy-chat', data);
