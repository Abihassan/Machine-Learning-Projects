import React, { useState, useRef, useEffect } from 'react';
import { Camera, Upload, AlertTriangle, ShieldCheck, RefreshCcw } from 'lucide-react';

export default function App() {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  // Initialize camera
  useEffect(() => {
    if (!result) startCamera();
    return () => stopCamera();
  }, [result]);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { facingMode: "environment" } 
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    } catch (err) {
      console.error("Camera access denied or unavailable.", err);
    }
  };

  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      videoRef.current.srcObject.getTracks().forEach(track => track.stop());
    }
  };

  const captureImage = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    canvas.toBlob((blob) => {
      const file = new File([blob], "capture.jpg", { type: "image/jpeg" });
      const previewUrl = URL.createObjectURL(blob);
      setImagePreview(previewUrl);
      analyzeImage(file);
    }, 'image/jpeg');
    
    stopCamera();
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const previewUrl = URL.createObjectURL(file);
      setImagePreview(previewUrl);
      analyzeImage(file);
      stopCamera();
    }
  };

  const analyzeImage = async (file) => {
    setIsAnalyzing(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      // Send to local FastAPI backend
      const response = await fetch('http://localhost:8000/analyze', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error("Error analyzing image:", error);
      alert("Failed to connect to backend. Make sure FastAPI is running on port 8000.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const resetScanner = () => {
    setResult(null);
    setImagePreview(null);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center">
      {/* Header */}
      <header className="w-full bg-emerald-600 text-white p-4 shadow-md flex items-center justify-center gap-2">
        <ShieldCheck size={24} />
        <h1 className="text-xl font-bold tracking-wide">CropGuard</h1>
      </header>

      <main className="w-full max-w-md p-4 flex flex-col gap-6 flex-grow">
        
        {/* Scanner / Result Area */}
        <div className="relative w-full aspect-[3/4] bg-black rounded-2xl overflow-hidden shadow-lg flex items-center justify-center">
          
          {!imagePreview ? (
            <video 
              ref={videoRef} 
              autoPlay 
              playsInline 
              className="absolute inset-0 w-full h-full object-cover"
            />
          ) : (
            <div className="relative w-full h-full">
              <img src={imagePreview} className="absolute inset-0 w-full h-full object-cover" alt="Captured leaf" />
              
              {/* Bounding Boxes */}
              {result && result.boxes.map((box, i) => (
                <div 
                  key={i}
                  className="absolute border-2 border-red-500 bg-red-500/20"
                  style={{
                    left: `${box.x}%`,
                    top: `${box.y}%`,
                    width: `${box.width}%`,
                    height: `${box.height}%`
                  }}
                />
              ))}
            </div>
          )}

          {/* Hidden Canvas for extracting image */}
          <canvas ref={canvasRef} className="hidden" />

          {/* Scanning Animation */}
          {isAnalyzing && (
            <div className="absolute inset-0 bg-emerald-900/40 flex items-center justify-center flex-col">
              <div className="w-full h-1 bg-emerald-400 animate-pulse shadow-[0_0_15px_#34d399] absolute top-1/2"></div>
              <p className="text-white font-semibold mt-10 animate-bounce">Analyzing Pathogens...</p>
            </div>
          )}
        </div>

        {/* Controls */}
        {!result && !isAnalyzing && (
          <div className="flex items-center justify-between px-4">
            <label className="p-4 bg-white rounded-full shadow-md cursor-pointer text-gray-600 hover:text-emerald-600 transition">
              <Upload size={24} />
              <input type="file" accept="image/*" className="hidden" onChange={handleFileUpload} />
            </label>
            
            <button 
              onClick={captureImage}
              className="w-20 h-20 bg-emerald-500 rounded-full border-4 border-white shadow-xl hover:scale-105 transition flex items-center justify-center text-white"
            >
              <Camera size={32} />
            </button>
            <div className="w-14" /> {/* Spacer for symmetry */}
          </div>
        )}

        {/* Results Dashboard */}
        {result && (
          <div className="bg-white p-5 rounded-2xl shadow-md border border-gray-100 flex flex-col gap-4 animate-fade-in">
            <div className="flex justify-between items-start">
              <div>
                <h2 className="text-lg font-bold text-gray-800">{result.disease}</h2>
                <p className="text-sm text-gray-500">Confidence: {result.confidence}%</p>
              </div>
              <span className={`px-3 py-1 rounded-full text-xs font-bold flex items-center gap-1 ${
                result.severity === 'High' ? 'bg-red-100 text-red-700' : 
                result.severity === 'Medium' ? 'bg-yellow-100 text-yellow-700' : 
                'bg-emerald-100 text-emerald-700'
              }`}>
                <AlertTriangle size={14} /> {result.severity}
              </span>
            </div>

            <div className="bg-gray-50 p-4 rounded-xl">
              <h3 className="text-sm font-semibold text-gray-700 mb-2">Recommended Actions:</h3>
              <ul className="text-sm text-gray-600 list-disc pl-5 space-y-1">
                {result.treatments.map((treatment, i) => (
                  <li key={i}>{treatment}</li>
                ))}
              </ul>
            </div>

            <button 
              onClick={resetScanner}
              className="w-full py-3 mt-2 bg-emerald-50 text-emerald-700 font-semibold rounded-xl flex items-center justify-center gap-2 hover:bg-emerald-100 transition"
            >
              <RefreshCcw size={18} /> Scan Another Leaf
            </button>
          </div>
        )}
      </main>
    </div>
  );
}