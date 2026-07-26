import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Send, Upload, Settings, Database, Bot } from 'lucide-react';

const API_URL = 'http://localhost:8000';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: { source: string; content: string }[];
}

export default function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [models, setModels] = useState<string[]>(['phi3']);
  const [selectedModel, setSelectedModel] = useState('phi3');
  const [uploading, setUploading] = useState(false);
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    fetchModels();
  }, []);

  const fetchModels = async () => {
    try {
      const res = await axios.get(`${API_URL}/models`);
      setModels(res.data.models);
      if (res.data.models.length > 0) setSelectedModel(res.data.models[0]);
    } catch (error) {
      console.error("Failed to fetch models", error);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    setUploading(true);
    try {
      await axios.post(`${API_URL}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      alert('Document processed and indexed successfully!');
    } catch (error) {
      console.error(error);
      alert('Failed to upload document.');
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleChat = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg: Message = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await axios.post(`${API_URL}/chat`, {
        query: userMsg.content,
        model: selectedModel
      });
      
      const assistantMsg: Message = { 
        role: 'assistant', 
        content: res.data.answer,
        sources: res.data.sources 
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (error) {
      console.error(error);
      setMessages((prev) => [...prev, { role: 'assistant', content: "Error connecting to local backend." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-gray-50 font-sans text-gray-800">
      {/* Sidebar Configurations */}
      <aside className="w-72 bg-white border-r p-4 flex flex-col justify-between">
        <div>
          <div className="flex items-center gap-2 mb-8 text-xl font-bold text-indigo-600">
            <Database size={24} />
            <span>Local RAG</span>
          </div>

          <div className="mb-6">
            <label className="flex items-center gap-2 text-sm font-semibold mb-2">
              <Settings size={16} /> Select LLM Model
            </label>
            <select 
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              className="w-full p-2 border rounded-md bg-gray-50 focus:ring-2 focus:ring-indigo-500 outline-none"
            >
              {models.map(m => <option key={m} value={m}>{m}</option>)}
            </select>
          </div>

          <div className="mb-6">
            <label className="flex items-center gap-2 text-sm font-semibold mb-2">
              <Upload size={16} /> Upload Notebook
            </label>
            <input 
              type="file" 
              ref={fileInputRef}
              accept=".txt,.md,.pdf"
              onChange={handleFileUpload}
              className="hidden"
            />
            <button 
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
              className="w-full flex items-center justify-center gap-2 p-2 bg-indigo-50 text-indigo-700 rounded-md hover:bg-indigo-100 transition"
            >
              {uploading ? 'Processing...' : 'Choose File'}
            </button>
            <p className="text-xs text-gray-400 mt-2">Supports .txt, .md, .pdf</p>
          </div>
        </div>
      </aside>

      {/* Main Chat Interface */}
      <main className="flex-1 flex flex-col">
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.length === 0 && (
            <div className="h-full flex flex-col items-center justify-center text-gray-400">
              <Bot size={48} className="mb-4 opacity-50" />
              <p>Upload a document and start querying your local database.</p>
            </div>
          )}
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-3xl rounded-xl p-4 shadow-sm ${msg.role === 'user' ? 'bg-indigo-600 text-white' : 'bg-white border text-gray-800'}`}>
                <p className="whitespace-pre-wrap">{msg.content}</p>
                
                {/* Render Sources */}
                {msg.sources && msg.sources.length > 0 && (
                  <div className="mt-4 pt-4 border-t border-gray-100">
                    <p className="text-xs font-bold text-gray-400 mb-2 uppercase">Sources Retrieved:</p>
                    <div className="space-y-2">
                      {msg.sources.map((src, i) => (
                        <details key={i} className="text-sm bg-gray-50 rounded p-2 text-gray-600">
                          <summary className="cursor-pointer font-medium text-xs">{src.source}</summary>
                          <p className="mt-2 text-xs italic">"{src.content}"</p>
                        </details>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
          {loading && (
             <div className="flex justify-start">
               <div className="bg-white border rounded-xl p-4 shadow-sm text-gray-500 animate-pulse">
                 Model is thinking...
               </div>
             </div>
          )}
        </div>

        {/* Chat Input */}
        <div className="p-4 bg-white border-t">
          <form onSubmit={handleChat} className="max-w-4xl mx-auto relative flex items-center">
            <input 
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={`Ask a question securely using ${selectedModel}...`}
              className="w-full p-4 pr-12 bg-gray-50 border rounded-full focus:ring-2 focus:ring-indigo-500 outline-none"
            />
            <button 
              type="submit" 
              disabled={loading || !input.trim()}
              className="absolute right-2 p-2 bg-indigo-600 text-white rounded-full hover:bg-indigo-700 disabled:opacity-50 transition"
            >
              <Send size={20} />
            </button>
          </form>
        </div>
      </main>
    </div>
  );
}