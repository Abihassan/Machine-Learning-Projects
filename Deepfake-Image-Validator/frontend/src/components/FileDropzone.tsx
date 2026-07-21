import React, { useState, type DragEvent } from 'react';
import { Upload, Image as ImageIcon } from 'lucide-react';

interface FileDropzoneProps {
  onFileSelect: (file: File) => void;
}

export const FileDropzone: React.FC<FileDropzoneProps> = ({ onFileSelect }) => {
  const [isDragActive, setIsDragActive] = useState(false);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") setIsDragActive(true);
    else if (e.type === "dragleave") setIsDragActive(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onFileSelect(e.dataTransfer.files[0]);
    }
  };

  return (
    <div
      onDragEnter={handleDrag}
      onDragOver={handleDrag}
      onDragLeave={handleDrag}
      onDrop={handleDrop}
      className={`border-2 border-dashed rounded-xl p-12 text-center transition-all cursor-pointer ${
        isDragActive ? 'border-indigo-500 bg-indigo-950/20' : 'border-slate-700 hover:border-slate-500 bg-slate-900/40'
      }`}
    >
      <input
        type="file"
        id="file-upload"
        className="hidden"
        accept="image/jpeg, image/png, image/webp"
        onChange={(e) => e.target.files && onFileSelect(e.target.files[0])}
      />
      <label htmlFor="file-upload" className="cursor-pointer flex flex-col items-center">
        <Upload className="h-12 w-12 text-indigo-400 mb-4 animate-pulse" />
        <p className="text-lg text-slate-200 font-medium">Drag & drop profile vector image here</p>
        <p className="text-sm text-slate-400 mt-1">Accepts PNG, JPEG, or WebP</p>
      </label>
    </div>
  );
};