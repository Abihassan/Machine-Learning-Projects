import React from 'react';
import { ProgressRing } from './ProgressRing';
import { ShieldCheck, ShieldAlert, RefreshCw } from 'lucide-react';

interface AnalysisResult {
  authenticityScore: number;
  verdict: string;
  explanation: string;
  heatmapImage: string;
}

interface DashboardProps {
  result: AnalysisResult;
  previewUrl: string;
  onReset: () => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ result, previewUrl, onReset }) => {
  const isSafe = result.authenticityScore >= 70;

  return (
    <div className="grid md:grid-cols-2 gap-8 items-start max-w-4xl mx-auto bg-slate-900/60 p-6 rounded-2xl border border-slate-800">
      <div className="space-y-4">
        <h3 className="text-sm font-semibold tracking-wider text-slate-400 uppercase">Analysis Matrix View</h3>
        <div className="relative group rounded-xl overflow-hidden border border-slate-700 bg-black aspect-square flex items-center justify-center">
          <img 
            src={result.heatmapImage} 
            alt="Artifact Analysis Heatmap" 
            className="w-full h-full object-cover transition-opacity duration-500" 
          />
          <div className="absolute bottom-3 left-3 bg-slate-950/80 px-3 py-1 text-xs rounded-md text-slate-300 backdrop-blur-sm border border-slate-800">
            Structural Anomaly Map
          </div>
        </div>
      </div>

      <div className="flex flex-col justify-between h-full space-y-6">
        <div>
          <h3 className="text-sm font-semibold tracking-wider text-slate-400 uppercase mb-4">Authenticity Metrics</h3>
          <div className="flex items-center gap-6 bg-slate-950/40 p-4 rounded-xl border border-slate-800/80">
            <ProgressRing score={result.authenticityScore} />
            <div>
              <div className="flex items-center gap-2">
                {isSafe ? <ShieldCheck className="text-emerald-400 w-5 h-5" /> : <ShieldAlert className="text-rose-400 w-5 h-5" />}
                <h4 className="text-xl font-bold text-white">{result.verdict}</h4>
              </div>
              <p className="text-sm text-slate-400 mt-1">Confidence Interval Target</p>
            </div>
          </div>
          <p className="text-slate-300 mt-6 leading-relaxed bg-slate-900/30 p-4 rounded-xl border border-slate-800">
            {result.explanation}
          </p>
        </div>

        <button
          onClick={onReset}
          className="w-full flex items-center justify-center gap-2 py-3 bg-slate-800 hover:bg-slate-700 transition-colors text-white font-medium rounded-xl border border-slate-700"
        >
          <RefreshCw className="w-4 h-4" /> Scan Another Image
        </button>
      </div>
    </div>
  );
};