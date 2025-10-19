/**
 * API service for communicating with the backend
 */

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || '/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// YAML operations
export const parseYAML = async (content) => {
  const response = await api.post('/parse', { content });
  return response.data;
};

export const validateYAML = async (content) => {
  const response = await api.post('/validate', { content });
  return response.data;
};

export const explainYAML = async (content, useLLM = false) => {
  const response = await api.post('/explain', { content, use_llm: useLLM });
  return response.data;
};

export const generateYAML = async (resourceType, config) => {
  const response = await api.post('/generate', {
    resource_type: resourceType,
    config: config,
  });
  return response.data;
};

// Settings operations
export const getSettings = async () => {
  const response = await api.get('/settings');
  return response.data;
};

export const getSetting = async (key) => {
  const response = await api.get(`/settings/${key}`);
  return response.data;
};

export const updateSetting = async (key, value) => {
  const response = await api.put('/settings', { key, value });
  return response.data;
};

// LLM configuration operations
export const getLLMConfigs = async () => {
  const response = await api.get('/llm/config');
  return response.data;
};

export const createLLMConfig = async (config) => {
  const response = await api.post('/llm/config', config);
  return response.data;
};

export const updateLLMConfig = async (id, config) => {
  const response = await api.put(`/llm/config/${id}`, config);
  return response.data;
};

export const deleteLLMConfig = async (id) => {
  const response = await api.delete(`/llm/config/${id}`);
  return response.data;
};

export const activateLLMConfig = async (id) => {
  const response = await api.post(`/llm/config/${id}/activate`);
  return response.data;
};

export const testLLMConnection = async (endpoint, apiKey, modelName = null) => {
  const response = await api.post('/llm/test', {
    endpoint,
    api_key: apiKey,
    model_name: modelName,
  });
  return response.data;
};

export default api;
