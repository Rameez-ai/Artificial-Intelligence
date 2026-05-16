import client from './client';

export const login    = (email, password)               => client.post('/api/auth/login',   { email, password });
export const signup   = (name, email, password, phone)  => client.post('/api/auth/signup',  { name, email, password, phone });
export const getProfile = ()                            => client.get('/api/auth/profile');
export const updateProfile = (data)                     => client.put('/api/auth/profile',  data);
