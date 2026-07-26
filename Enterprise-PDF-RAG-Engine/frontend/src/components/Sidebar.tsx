import React, { useEffect, useState, useRef } from 'react';
import axios from 'axios';
import { UploadCloud, FileText, Loader2, Server } from 'lucide-react';

interface SidebarProps {
  documents: string[];
  setDocuments: React.Dispatch<React.SetStateAction<string[]>>;
}

const Sidebar: React.FC<SidebarProps> = ({ documents, setDocuments }) => {
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchDocuments = async () => {
    try {
      const res = await axios.get('http://localhost:8000/api/documents');
      setDocuments(res.data.documents);
    } catch (error) {
      console.error("Failed to fetch documents", error);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);
    
    setIsUploading(true);
    try {
      await axios.post('http://localhost:8000/api/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      fetchDocuments();
    } catch (error) {
      console.error("Upload failed", error);
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  return (
    <div className="w-80 bg-slate-900 text-slate-300 flex flex-col h-full border-r border-slate-800">
      <div className="p-6">
        <h2 className="text-sm uppercase tracking-wider font-semibold text-slate-500 mb-4 flex items-center gap-2">
          <Server size={16} /> Knowledge Base
        </h2>
        
        <div 
          className="border-2 border-dashed border-slate-700 rounded-xl p-6 text-center cursor-pointer hover:bg-slate-800 transition-colors"
          onClick={() => fileInputRef.current?.click()}
        >
          <input 
            type="file" 
            accept=".pdf" 
            className="hidden" 
            ref={fileInputRef} 
            onChange={handleFileUpload} 
          />
          {isUploading ? (
            <div className="flex flex-col items-center gap-2">
              <Loader2 className="animate-spin text-blue-500" size={24} />
              <span className="text-sm">Indexing locally...</span>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-2">
              <UploadCloud size={28} className="text-slate-400" />
              <span className="text-sm font-medium">Upload PDF</span>
              <span className="text-xs text-slate-500">Max 50MB</span>
            </div>
          )}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-4">
        <h3 className="text-xs font-semibold text-slate-500 mb-3 px-2">INDEXED FILES</h3>
        <ul className="space-y-1">
          {documents.map((doc, idx) => (
            <li key={idx} className="flex items-center gap-3 px-3 py-2 bg-slate-800/50 rounded-lg text-sm">
              <FileText size={16} className="text-blue-400 flex-shrink-0" />
              <span className="truncate">{doc}</span>
            </li>
          ))}
          {documents.length === 0 && (
            <p className="text-sm text-slate-500 px-2 italic">No documents indexed yet.</p>
          )}
        </ul>
      </div>
    </div>
  );
};

export default Sidebar;