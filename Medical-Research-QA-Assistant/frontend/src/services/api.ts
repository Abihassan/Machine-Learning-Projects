import axios from 'axios';
import type { QueryResponse } from '../types';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
  // Set a generous timeout (e.g., 2 minutes) for local LLM inference
  timeout: 120000, 
});

export const askMedicalQuestion = async (question: string): Promise<QueryResponse> => {
  try {
    const response = await apiClient.post<QueryResponse>('/ask', {
      question,
      max_papers: 5
    });
    return response.data;
  } catch (error: any) {
    if (error.code === 'ECONNABORTED') {
      throw new Error("The local model took too long to respond. Please try a simpler query or check your hardware resources.");
    }
    if (error.response?.data?.detail) {
      throw new Error(error.response.data.detail);
    }
    throw new Error("An unexpected error occurred while connecting to the local backend.");
  }
};