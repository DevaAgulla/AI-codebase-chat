import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const client = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const analyzeRepository = async (repoUrl, branch = null) => {
  const response = await client.post('/api/analyze', {
    repo_url: repoUrl,
    branch: branch,
  });
  return response.data;
};

export const generateReadme = async (repoUrl = null, analysis = null) => {
  const response = await client.post('/api/generate-readme', {
    repo_url: repoUrl,
    analysis: analysis,
  });
  return response.data;
};

export const askQuestion = async (question, repoUrl = null, analysis = null) => {
  const response = await client.post('/api/ask', {
    question: question,
    repo_url: repoUrl,
    analysis: analysis,
  });
  return response.data;
};

export default client;
