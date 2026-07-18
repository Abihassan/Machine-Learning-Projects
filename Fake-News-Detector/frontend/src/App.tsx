import { useState } from 'react';

interface PredictionResult {
  prediction: 'REAL' | 'FAKE';
  confidence: number;
}

export default function App() {
  const [text, setText] = useState('');
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleAnalyze = async () => {
    if (!text.trim()) {
      setError('Please enter some text to analyze.');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await fetch('http://localhost:8000/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      });

      if (!response.ok) throw new Error('Failed to reach the server.');

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError('Error connecting to the backend. Ensure your FastAPI server is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center p-4 sm:p-8 font-sans text-slate-900 selection:bg-indigo-100 selection:text-indigo-900">
      
      <main className="w-full max-w-3xl">
        {/* Header Section */}
        <div className="mb-10 text-center space-y-4">
          <div className="inline-flex items-center justify-center px-3 py-1 rounded-full bg-indigo-50 border border-indigo-100 text-sm font-medium text-indigo-600 mb-4">
            <span className="flex h-2 w-2 rounded-full bg-indigo-500 mr-2 animate-pulse"></span>
            Machine Learning Powered
          </div>
          <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight text-slate-900">
            Fake News <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-violet-500">Detector</span>
          </h1>
          <p className="text-lg text-slate-500 max-w-xl mx-auto">
            Analyze headlines and news snippets instantly to verify authenticity using our trained NLP model.
          </p>
        </div>

        {/* Primary Interactive Card */}
        <div className="bg-white rounded-3xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-slate-100 overflow-hidden transition-all duration-300">
          <div className="p-6 sm:p-10">
            <div className="space-y-6">
              
              {/* Text Area */}
              <div className="relative group">
                <textarea
                  rows={4}
                  className="w-full bg-slate-50 border border-slate-200 text-slate-700 rounded-2xl p-5 outline-none transition-all duration-200 focus:bg-white focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-400 placeholder-slate-400 resize-none text-lg"
                  placeholder="Paste a headline or short claim here..."
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                />
              </div>
              
              {/* Error Message */}
              {error && (
                <div className="flex items-center gap-3 p-4 text-sm text-rose-600 bg-rose-50 border border-rose-100 rounded-xl">
                  <svg className="w-5 h-5 shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                  <p className="font-medium">{error}</p>
                </div>
              )}

              {/* Action Button */}
              <button
                onClick={handleAnalyze}
                disabled={loading}
                className={`w-full relative overflow-hidden group flex items-center justify-center py-4 rounded-xl font-bold text-white transition-all duration-300 ${
                  loading 
                    ? 'bg-slate-300 cursor-not-allowed' 
                    : 'bg-slate-900 hover:bg-slate-800 hover:shadow-xl hover:shadow-slate-900/20 hover:-translate-y-0.5'
                }`}
              >
                {loading ? (
                  <span className="flex items-center gap-2 text-slate-600">
                    <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Analyzing Patterns...
                  </span>
                ) : (
                  'Analyze Text'
                )}
              </button>
            </div>
          </div>

          {/* Results Dashboard - Renders conditionally with animation */}
          {result && (
            <div className="bg-slate-50 border-t border-slate-100 p-6 sm:p-10 animate-slide-up">
              <div className="flex flex-col items-center">
                
                <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-6">
                  Analysis Result
                </h3>
                
                {/* Verdict Badge */}
                <div
                  className={`inline-flex items-center justify-center px-8 py-3 rounded-full text-3xl font-black tracking-tight mb-8 shadow-sm ${
                    result.prediction === 'REAL' 
                      ? 'bg-emerald-100 text-emerald-700 border-2 border-emerald-200' 
                      : 'bg-rose-100 text-rose-700 border-2 border-rose-200'
                  }`}
                >
                  {result.prediction === 'REAL' ? (
                    <svg className="w-8 h-8 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" /></svg>
                  ) : (
                    <svg className="w-8 h-8 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
                  )}
                  {result.prediction}
                </div>
                
                {/* Progress Bar Area */}
                <div className="w-full max-w-md bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
                  <div className="flex justify-between items-end mb-3">
                    <span className="text-sm font-semibold text-slate-500">Model Confidence</span>
                    <span className={`text-2xl font-bold ${result.prediction === 'REAL' ? 'text-emerald-600' : 'text-rose-600'}`}>
                      {result.confidence}%
                    </span>
                  </div>
                  
                  <div className="w-full bg-slate-100 rounded-full h-3 overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-1000 ease-out ${
                        result.prediction === 'REAL' ? 'bg-emerald-500' : 'bg-rose-500'
                      }`}
                      style={{ width: `${result.confidence}%` }}
                    ></div>
                  </div>
                </div>

              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}