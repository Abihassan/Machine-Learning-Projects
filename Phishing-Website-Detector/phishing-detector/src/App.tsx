import React, { useState } from 'react';
import { Shield, ShieldAlert, Activity, Search, AlertTriangle, Code } from 'lucide-react';
import { analyzeUrl } from './api/mockApi';
import type { AnalysisResult } from './api/types';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';

function App() {
  const [urlInput, setUrlInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [showJson, setShowJson] = useState(false);

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!urlInput) return;
    
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await analyzeUrl(urlInput);
      setResult(data);
    } catch (err: any) {
      setError(err.message || 'Analysis failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getVerdictColor = (verdict: string) => {
    switch(verdict) {
      case 'Safe': return 'text-cyan-400';
      case 'Suspicious': return 'text-yellow-400';
      case 'Malicious': return 'text-red-500';
      default: return 'text-gray-400';
    }
  };

  const gaugeData = result ? [
    { name: 'Score', value: result.trustScore },
    { name: 'Remaining', value: 100 - result.trustScore }
  ] : [];
  
  const gaugeColor = result?.verdict === 'Safe' ? '#22d3ee' : result?.verdict === 'Suspicious' ? '#facc15' : '#ef4444';

  return (
    <div className="min-h-screen flex flex-col font-sans">
      {/* Navbar */}
      <nav className="border-b border-gray-800 bg-gray-950 p-4">
        <div className="max-w-6xl mx-auto flex items-center gap-2">
          <Activity className="text-cyan-400" />
          <h1 className="text-xl font-bold tracking-wider text-gray-100">PHISH<span className="text-cyan-400">GUARD</span></h1>
        </div>
      </nav>

      {/* Main Content */}
      <main className="flex-grow p-6 flex flex-col items-center">
        
        {/* Search Bar */}
        <div className="w-full max-w-3xl mt-10 mb-12">
          <h2 className="text-3xl font-bold text-center mb-6 text-gray-200">Analyze URL Security</h2>
          <form onSubmit={handleAnalyze} className="relative flex items-center">
            <Search className="absolute left-4 text-gray-500" size={20} />
            <input
              type="text"
              className="w-full bg-gray-900 border border-gray-700 text-gray-100 rounded-lg py-4 pl-12 pr-32 focus:outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 transition-all placeholder-gray-600"
              placeholder="https://example.com"
              value={urlInput}
              onChange={(e) => setUrlInput(e.target.value)}
            />
            <button
              type="submit"
              disabled={loading}
              className="absolute right-2 bg-cyan-600 hover:bg-cyan-500 text-white px-6 py-2 rounded-md font-medium transition-colors disabled:opacity-50"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mx-auto"></div>
              ) : 'Analyze'}
            </button>
          </form>
          {error && (
            <div className="mt-4 p-3 bg-red-950 border border-red-800 text-red-400 rounded-md flex items-center gap-2">
              <AlertTriangle size={18} />
              {error}
            </div>
          )}
        </div>

        {/* Dashboard Results */}
        {result && (
          <div className="w-full max-w-6xl grid grid-cols-1 md:grid-cols-3 gap-6 animate-fade-in">
            
            {/* Scoring & Verdict (Left Column) */}
            <div className="bg-gray-900 border border-gray-800 p-6 rounded-xl shadow-lg flex flex-col items-center justify-center relative overflow-hidden">
              <div className="absolute top-0 w-full h-1 bg-gradient-to-r from-transparent via-gray-700 to-transparent"></div>
              <h3 className="text-lg font-semibold text-gray-400 mb-2">Trust Score</h3>
              
              <div className="w-48 h-48 relative">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={gaugeData}
                      cx="50%"
                      cy="50%"
                      startAngle={180}
                      endAngle={0}
                      innerRadius={60}
                      outerRadius={80}
                      paddingAngle={0}
                      dataKey="value"
                      stroke="none"
                    >
                      <Cell fill={gaugeColor} />
                      <Cell fill="#1f2937" />
                    </Pie>
                  </PieChart>
                </ResponsiveContainer>
                <div className="absolute inset-0 flex items-center justify-center flex-col mt-4">
                  <span className="text-4xl font-bold">{result.trustScore}</span>
                  <span className="text-xs text-gray-500">/ 100</span>
                </div>
              </div>

              <div className="flex items-center gap-2 mt-4">
                {result.verdict === 'Safe' ? <Shield className="text-cyan-400" size={24} /> : <ShieldAlert className={getVerdictColor(result.verdict)} size={24} />}
                <span className={`text-2xl font-bold ${getVerdictColor(result.verdict)}`}>
                  {result.verdict}
                </span>
              </div>
            </div>

            {/* URL Structure (Middle Column) */}
            <div className="bg-gray-900 border border-gray-800 p-6 rounded-xl shadow-lg">
              <h3 className="text-lg font-semibold text-gray-300 mb-4 border-b border-gray-800 pb-2">URL Structure</h3>
              <ul className="space-y-3 text-sm">
                <li className="flex justify-between">
                  <span className="text-gray-400">Unusually Long:</span>
                  <span className={result.structure.isLong ? 'text-red-400' : 'text-cyan-400'}>{result.structure.isLong ? 'Yes' : 'No'}</span>
                </li>
                <li className="flex justify-between">
                  <span className="text-gray-400">Contains '@':</span>
                  <span className={result.structure.hasAtSymbol ? 'text-red-400' : 'text-cyan-400'}>{result.structure.hasAtSymbol ? 'Yes' : 'No'}</span>
                </li>
                <li className="flex justify-between">
                  <span className="text-gray-400">IP as Domain:</span>
                  <span className={result.structure.isIpAddress ? 'text-red-400' : 'text-cyan-400'}>{result.structure.isIpAddress ? 'Yes' : 'No'}</span>
                </li>
                <li className="flex justify-between">
                  <span className="text-gray-400">Subdomains:</span>
                  <span className={result.structure.subdomainCount > 2 ? 'text-yellow-400' : 'text-cyan-400'}>{result.structure.subdomainCount}</span>
                </li>
                <li className="flex justify-between">
                  <span className="text-gray-400">Suspicious TLD:</span>
                  <span className={result.structure.suspiciousTld ? 'text-red-400' : 'text-cyan-400'}>{result.structure.suspiciousTld ? 'Yes' : 'No'}</span>
                </li>
              </ul>
            </div>

            {/* Security Features (Right Column) */}
            <div className="bg-gray-900 border border-gray-800 p-6 rounded-xl shadow-lg flex flex-col">
              <h3 className="text-lg font-semibold text-gray-300 mb-4 border-b border-gray-800 pb-2">Security Posture</h3>
              <ul className="space-y-3 text-sm flex-grow">
                <li className="flex justify-between">
                  <span className="text-gray-400">HTTPS Secured:</span>
                  <span className={!result.security.hasHttps ? 'text-red-400' : 'text-cyan-400'}>{result.security.hasHttps ? 'Yes' : 'No'}</span>
                </li>
                <li className="flex justify-between">
                  <span className="text-gray-400">Valid SSL:</span>
                  <span className={!result.security.validSsl ? 'text-red-400' : 'text-cyan-400'}>{result.security.validSsl ? 'Yes' : 'No'}</span>
                </li>
                <li className="flex justify-between">
                  <span className="text-gray-400">Domain Age (Days):</span>
                  <span className={result.security.domainAgeDays < 30 ? 'text-yellow-400' : 'text-cyan-400'}>{result.security.domainAgeDays}</span>
                </li>
                <li className="flex justify-between">
                  <span className="text-gray-400">Masked Redirects:</span>
                  <span className={result.security.hasRedirects ? 'text-yellow-400' : 'text-cyan-400'}>{result.security.hasRedirects ? 'Detected' : 'Clear'}</span>
                </li>
              </ul>
              
              <button 
                onClick={() => setShowJson(!showJson)}
                className="mt-4 flex items-center justify-center gap-2 w-full py-2 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded text-sm transition-colors"
              >
                <Code size={16} /> {showJson ? 'Hide' : 'View'} Raw Data
              </button>
            </div>

            {/* JSON Debug View */}
            {showJson && (
              <div className="col-span-1 md:col-span-3 bg-gray-950 border border-gray-800 p-4 rounded-lg overflow-x-auto">
                <pre className="text-xs text-green-400 font-mono">
                  {JSON.stringify(result, null, 2)}
                </pre>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;