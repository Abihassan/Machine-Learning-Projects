import React, { useEffect, useRef, useState } from 'react';

// Define the structure for incoming WebSocket data
interface DetectionLog {
  label: string;
  box: number[];
}

interface StreamData {
  frame: string;
  logs: DetectionLog[];
}

export default function App() {
  const [logs, setLogs] = useState<string[]>([]);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const imgRef = useRef<HTMLImageElement>(null);

  useEffect(() => {
    // Establish WebSocket Connection
    const ws = new WebSocket('ws://localhost:8000/ws/video');
    
    ws.onopen = () => setIsConnected(true);
    ws.onclose = () => setIsConnected(false);
    
    ws.onmessage = (event: MessageEvent) => {
      try {
        const data: StreamData = JSON.parse(event.data);
        
        // Render incoming Base64 frame
        if (imgRef.current && data.frame) {
          imgRef.current.src = `data:image/jpeg;base64,${data.frame}`;
        }
        
        // Process new violations, pushing them to the top of the log array
        if (data.logs.length > 0) {
          const newLogs = data.logs.map(
            (log) => `${new Date().toLocaleTimeString()} - ${log.label}`
          );
          setLogs((prev) => [...newLogs, ...prev].slice(0, 20)); // Retain only the last 20 logs
        }
      } catch (error) {
        console.error("Error parsing stream data:", error);
      }
    };

    return () => ws.close();
  }, []);

  return (
    <div className="min-h-screen bg-slate-100 p-8 font-sans">
      <div className="max-w-7xl mx-auto">
        <header className="mb-8 border-b pb-4 flex justify-between items-end">
          <h1 className="text-3xl font-bold text-slate-800">
            PPE Compliance Dashboard
          </h1>
          <div className="flex items-center text-sm font-medium">
            Status: 
            <span className={`ml-2 px-3 py-1 rounded-full text-white ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}>
              {isConnected ? 'Live' : 'Disconnected'}
            </span>
          </div>
        </header>
        
        <div className="flex flex-col lg:flex-row gap-6">
          {/* Main Video Stream Panel */}
          <div className="flex-grow bg-white p-6 rounded-xl shadow-sm border border-slate-200">
            <h2 className="text-lg font-semibold mb-4 text-slate-700 flex items-center">
              Live Edge Inference Stream
            </h2>
            <div className="aspect-video bg-black rounded-lg overflow-hidden flex items-center justify-center">
              {isConnected ? (
                 <img ref={imgRef} className="w-full h-full object-contain" alt="Live Stream" />
              ) : (
                <p className="text-slate-500">Waiting for backend connection...</p>
              )}
            </div>
          </div>

          {/* Incident Logging Panel */}
          <div className="w-full lg:w-96 bg-white p-6 rounded-xl shadow-sm border border-slate-200 flex flex-col">
            <h2 className="text-lg font-semibold mb-4 text-slate-700">Incident Logs</h2>
            <div className="flex-1 overflow-y-auto bg-slate-50 rounded-lg p-3 border border-slate-100">
              {logs.length === 0 ? (
                <p className="text-slate-500 text-sm text-center mt-10">Monitoring active. No violations detected.</p>
              ) : (
                <ul className="space-y-3">
                  {logs.map((log, index) => (
                    <li key={index} className="text-sm bg-red-50 text-red-700 p-3 rounded-md border border-red-200 shadow-sm">
                      {log}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}