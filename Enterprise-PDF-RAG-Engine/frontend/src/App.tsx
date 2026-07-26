import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import ChatWindow from './components/ChatWindow';

const App: React.FC = () => {
  const [documents, setDocuments] = useState<string[]>([]);

  return (
    <div className="flex h-screen bg-gray-50 font-sans text-slate-800">
      <Sidebar documents={documents} setDocuments={setDocuments} />
      <main className="flex-1 flex flex-col relative bg-white shadow-xl z-10">
        <header className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
          <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-600">
            Enterprise RAG Assistant
          </h1>
          <span className="text-xs font-semibold px-3 py-1 bg-green-100 text-green-700 rounded-full flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
            Local Secure Mode
          </span>
        </header>
        <ChatWindow />
      </main>
    </div>
  );
};

export default App;