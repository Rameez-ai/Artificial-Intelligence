import client from './client';

export const sendMessage   = (message) => client.post('/api/chatbot/message', { message });
export const getChatHistory= ()        => client.get('/api/chatbot/history');
export const clearHistory  = ()        => client.delete('/api/chatbot/history');
