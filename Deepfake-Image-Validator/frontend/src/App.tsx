import { useState } from 'react';
import { FileDropzone } from './components/FileDropzone';
import { Dashboard } from './components/Dashboard';
import { ShieldCheck, Cpu } from 'lucide-react';

export default function App() {
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any | null>(null);

  const handleFileSelect = async (selectedFile: File) => {
    setFile(selectedFile);
    setPreviewUrl(URL.createObjectURL(selectedFile));
    setLoading(true);
    setResult(null);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch('http://localhost:8000/api/analyze', {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) throw new Error('Network error or invalid analysis context.');
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error(error);
      alert('Analysis error occurred. Verify that the backend server is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-between selection:bg-indigo-500/30">
      <header className="border-b border-slate-900 bg-slate-950/80 backdrop-blur sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-indigo-500/10 rounded-lg border border-indigo-500/20">
              <ShieldCheck className="w-6 h-6 text-indigo-400" />
            </div>
            <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
              Deepfake Validator
            </span>
          </div>
          <div className="flex items-center gap-2 text-xs text-slate-400 bg-slate-900 px-3 py-1.5 rounded-full border border-slate-800">
            <Cpu className="w-3.5 h-3.5 text-emerald-400 animate-pulse" /> Live Verification Engine active
          </div>
        </div>
      </header>

      <main className="flex-grow max-w-6xl w-full mx-auto px-6 py-12 flex flex-col justify-center">
        {!file && !loading && (
          <div className="max-w-xl mx-auto w-full space-y-6">
            <div className="text-center space-y-2">
              <h1 className="text-4xl font-black text-white tracking-tight">Verify Profile Authenticity</h1>
              <p className="text-slate-400">Upload profile assets to scan for biometric dissonance and generative AI artifacts.</p>
            </div>
            <FileDropzone onFileSelect={handleFileSelect} />
          </div>
        )}

        {loading && (
          <div className="flex flex-col items-center justify-center py-20 space-y-4">
            <div className="relative w-20 h-20">
              <div className="absolute inset-0 rounded-full border-4 border-indigo-500/20"></div>
              <div className="absolute inset-0 rounded-full border-4 border-t-indigo-400 animate-spin"></div>
            </div>
            <p className="text-indigo-300 font-medium tracking-wide animate-pulse">Running Artifact Analysis Metrics...</p>
          </div>
        )}

        {result && !loading && (
          <Dashboard 
            result={result} 
            previewUrl={previewUrl} 
            onReset={() => { setFile(null); setResult(null); setPreviewUrl(''); }} 
          />
        )}
      </main>

      <footer className="border-t border-slate-900 py-6 text-center text-xs text-slate-500">
        Deepfake Image Verification Framework • Secure Local Processing Pipeline
      </footer>
    </div>
  );
}