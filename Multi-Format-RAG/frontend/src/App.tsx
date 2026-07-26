import React, { useState, useRef } from 'react';

export default function App() {
  const [file, setFile] = useState<File | null>(null);
  const [uploadStatus, setUploadStatus] = useState<string>('');
  const [query, setQuery] = useState<string>('');
  const [chatHistory, setChatHistory] = useState<{role: string, text: string, sources?: string[]}[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setUploadStatus('Uploading and processing...');
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      setUploadStatus(data.message || 'Upload successful');
      setFile(null);
      if (fileInputRef.current) fileInputRef.current.value = '';
    } catch (err) {
      setUploadStatus('Upload failed. Check backend logs.');
    }
  };

  const handleChat = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    const userMessage = query;
    setQuery('');
    setChatHistory(prev => [...prev, { role: 'user', text: userMessage }]);
    setIsLoading(true);

    try {
      const res = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: userMessage }),
      });
      const data = await res.json();
      
      setChatHistory(prev => [...prev, { 
        role: 'assistant', 
        text: data.response, 
        sources: data.sources 
      }]);
    } catch (err) {
      setChatHistory(prev => [...prev, { role: 'assistant', text: 'Error connecting to the backend.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8 font-sans">
      <div className="max-w-4xl mx-auto space-y-8">
        
        <header className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <h1 className="text-2xl font-bold text-gray-800">Multi-Format RAG Engine</h1>
          <p className="text-gray-500">Query your text, PDFs, audio, and images privately.</p>
        </header>

        <section className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <h2 className="text-lg font-semibold mb-4">1. Ingest Data</h2>
          <form onSubmit={handleFileUpload} className="flex items-center gap-4">
            <input 
              type="file" 
              ref={fileInputRef}
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 cursor-pointer"
            />
            <button 
              type="submit" 
              disabled={!file}
              className="bg-blue-600 text-white px-6 py-2 rounded-full hover:bg-blue-700 disabled:opacity-50"
            >
              Process File
            </button>
          </form>
          {uploadStatus && <p className="mt-4 text-sm text-gray-600 font-medium">{uploadStatus}</p>}
        </section>

        <section className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 h-[500px] flex flex-col">
          <h2 className="text-lg font-semibold mb-4">2. Query Index</h2>
          
          <div className="flex-1 overflow-y-auto mb-4 space-y-4 pr-2">
            {chatHistory.map((msg, idx) => (
              <div key={idx} className={`p-4 rounded-xl max-w-[80%] ${msg.role === 'user' ? 'bg-blue-600 text-white ml-auto' : 'bg-gray-100 text-gray-800 mr-auto'}`}>
                <p className="whitespace-pre-wrap">{msg.text}</p>
                {msg.sources && msg.sources.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-300 text-xs text-gray-500">
                    <strong>Sources: </strong> {msg.sources.join(', ')}
                  </div>
                )}
              </div>
            ))}
            {isLoading && <div className="text-gray-400 text-sm italic">Synthesizing response...</div>}
          </div>

          <form onSubmit={handleChat} className="flex gap-2">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask a question about your files..."
              className="flex-1 border border-gray-300 rounded-full px-4 py-2 focus:outline-none focus:border-blue-500"
            />
            <button type="submit" className="bg-gray-800 text-white px-6 py-2 rounded-full hover:bg-gray-900">
              Send
            </button>
          </form>
        </section>

      </div>
    </div>
  );
}