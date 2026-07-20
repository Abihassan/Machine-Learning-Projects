// Replace the entire contents of src/api/mockApi.ts with this:
import type { AnalysisResult } from './types';

export const analyzeUrl = async (url: string): Promise<AnalysisResult> => {
  try {
    const response = await fetch('http://127.0.0.1:8000/api/analyze', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to analyze URL');
    }

    const data: AnalysisResult = await response.json();
    return data;
  } catch (error) {
    console.error("API Error:", error);
    throw new Error("Unable to reach the analysis server. Ensure the backend is running.");
  }
};