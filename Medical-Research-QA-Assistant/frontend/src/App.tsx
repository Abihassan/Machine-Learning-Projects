import React, { useState, useRef, useEffect } from 'react';
import { Send, Stethoscope, Loader2, BookOpen, AlertCircle } from 'lucide-react';
import type { ChatMessage } from './types';
import { askMedicalQuestion } from './services/api';

function App() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: input.trim(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await askMedicalQuestion(userMsg.content);
      
      const aiMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: response.answer,
        sources: response.sources,
      };
      
      setMessages((prev) => [...prev, aiMsg]);
    } catch (error: any) {
      const errorMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: error.message || "Failed to fetch response.",
        error: true
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-slate-50 font-sans text-slate-900">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 px-6 py-4 flex items-center shadow-sm z-10">
        <div className="bg-blue-100 p-2 rounded-lg mr-3">
          <Stethoscope className="text-blue-600 w-6 h-6" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-slate-800">Medical RAG Assistant</h1>
          <p className="text-xs text-slate-500">100% Local • Privacy-First • Context-Verified</p>
        </div>
      </header>

      {/* Chat Area */}
      <main className="flex-1 overflow-y-auto p-6 flex flex-col gap-6">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-slate-400 opacity-70">
            <BookOpen className="w-16 h-16 mb-4" />
            <p className="text-lg">Ask a medical research question to begin.</p>
            <p className="text-sm mt-2">Example: "What are the latest treatments for type 2 diabetes?"</p>
          </div>
        )}

        {messages.map((msg) => (
          <div key={msg.id} className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-3xl rounded-2xl p-5 shadow-sm ${
              msg.type === 'user' ? 'bg-blue-600 text-white' : 
              msg.error ? 'bg-red-50 border border-red-200 text-red-800' : 'bg-white border border-slate-200'
            }`}>
              
              {msg.error && <AlertCircle className="w-5 h-5 inline-block mr-2 mb-1" />}
              
              {/* Message Content */}
              <div className="whitespace-pre-wrap leading-relaxed">
                {msg.content}
              </div>

              {/* Citations/Sources Dropdown */}
              {msg.sources && msg.sources.length > 0 && (
                <div className="mt-4 pt-4 border-t border-slate-100">
                  <h4 className="text-sm font-semibold text-slate-500 mb-3 flex items-center">
                    <BookOpen className="w-4 h-4 mr-2" />
                    Verified PubMed Sources
                  </h4>
                  <div className="flex flex-col gap-3">
                    {msg.sources.map((source, idx) => (
                      <a 
                        key={idx}
                        href={`https://pubmed.ncbi.nlm.nih.gov/${source.pmid}/`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block bg-slate-50 p-3 rounded-lg hover:bg-blue-50 transition-colors border border-slate-100"
                      >
                        <div className="text-sm font-medium text-blue-700 mb-1">
                          [PMID: {source.pmid}] {source.title}
                        </div>
                        <div className="text-xs text-slate-500 line-clamp-2">
                          {source.snippet}
                        </div>
                      </a>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}

        {/* Loading Indicator */}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm flex items-center space-x-3 text-slate-500">
              <Loader2 className="w-5 h-5 animate-spin text-blue-600" />
              <span className="text-sm">Querying PubMed and generating local insights... (this may take a moment)</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </main>

      {/* Input Area */}
      <footer className="bg-white border-t border-slate-200 p-4">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto relative">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isLoading}
            placeholder="Ask a medical question..."
            className="w-full bg-slate-50 border border-slate-300 rounded-full py-4 pl-6 pr-14 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 transition-shadow"
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="absolute right-2 top-2 p-2 bg-blue-600 text-white rounded-full hover:bg-blue-700 disabled:bg-slate-300 transition-colors"
          >
            <Send className="w-5 h-5" />
          </button>
        </form>
      </footer>
    </div>
  );
}

export default App;