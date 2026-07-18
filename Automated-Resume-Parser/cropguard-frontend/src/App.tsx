import React, { useState } from 'react';

interface ContactInfo {
  name: string;
  email: string;
  phone: string;
}

interface WorkExperience {
  role_title: string;
  company: string;
  date_range: string;
  description: string;
}

interface Education {
  degree: string;
  institution: string;
  year: string;
}

interface ParsedData {
  contact_info: ContactInfo;
  skills: string[];
  work_experience: WorkExperience[];
  education: Education[];
}

export default function App() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [data, setData] = useState<ParsedData | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    setError(null);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://127.0.0.1:8000/api/parse', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to parse the uploaded document.');
      }

      const result: ParsedData = await response.json();
      setData(result);
    } catch (err: any) {
      setError(err.message || 'Something went wrong processing your document.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 font-sans p-6 sm:p-12">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header Block */}
        <header className="border-b border-gray-200 pb-6">
          <h1 className="text-3xl font-extrabold tracking-tight text-gray-900">Automated Resume Parser</h1>
          <p className="text-gray-500 mt-2">Upload engineering or technical resumes to extract structural data fields directly using zero-shot inference pipelines.</p>
        </header>

        {/* Upload Form Panel */}
        <section className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
          <form onSubmit={handleUpload} className="flex flex-col sm:flex-row items-center gap-4">
            <div className="w-full flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-2">Select Resume Document (PDF)</label>
              <input 
                type="file" 
                accept=".pdf"
                onChange={handleFileChange}
                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2.5 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100 cursor-pointer border border-gray-300 rounded-lg p-1"
              />
            </div>
            <button
              type="submit"
              disabled={!file || loading}
              className="w-full sm:w-auto mt-7 px-6 py-2.5 bg-indigo-600 text-white rounded-md text-sm font-semibold hover:bg-indigo-700 disabled:bg-gray-300 transition-colors shadow-sm"
            >
              {loading ? 'Processing inference...' : 'Parse Document'}
            </button>
          </form>
          {error && <p className="text-red-600 text-sm mt-3 font-medium">{error}</p>}
        </section>

        {/* Output Section Results View */}
        {data && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Left Column Contact + Skills info */}
            <div className="space-y-6 lg:col-span-1">
              <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm space-y-4">
                <h3 className="text-lg font-bold text-gray-800 border-b pb-2">Candidate Context</h3>
                <div>
                  <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Extracted Name</label>
                  <p className="text-base font-medium text-gray-900">{data.contact_info.name}</p>
                </div>
                <div>
                  <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Email Address</label>
                  <p className="text-base font-medium text-gray-900 break-all">{data.contact_info.email}</p>
                </div>
                <div>
                  <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Phone Field</label>
                  <p className="text-base font-medium text-gray-900">{data.contact_info.phone}</p>
                </div>
              </div>

              <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
                <h3 className="text-lg font-bold text-gray-800 border-b pb-3 mb-3">Core Skills Chips</h3>
                <div className="flex flex-wrap gap-2">
                  {data.skills.map((skill, index) => (
                    <span key={index} className="px-3 py-1 bg-gray-100 border border-gray-200 text-gray-700 text-xs font-semibold rounded-full tracking-wide">
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Right Tables Container Columns */}
            <div className="lg:col-span-2 space-y-8">
              {/* Experience Table Block */}
              <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
                <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
                  <h3 className="text-lg font-bold text-gray-800">Extracted Work Experience</h3>
                </div>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200 text-left text-sm">
                    <thead className="bg-gray-100 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                      <tr>
                        <th className="px-6 py-3">Role / Company</th>
                        <th className="px-6 py-3">Timeline</th>
                        <th className="px-6 py-3">Context Description Summary</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200 bg-white">
                      {data.work_experience.map((exp, i) => (
                        <tr key={i} className="align-top hover:bg-gray-50 transition-colors">
                          <td className="px-6 py-4">
                            <div className="font-semibold text-gray-900">{exp.role_title}</div>
                            <div className="text-xs text-indigo-600 font-medium">{exp.company}</div>
                          </td>
                          <td className="px-6 py-4 text-gray-600 whitespace-nowrap font-medium text-xs">{exp.date_range}</td>
                          <td className="px-6 py-4 text-gray-500 text-xs leading-relaxed max-w-xs sm:max-w-md">{exp.description}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Education Table Block */}
              <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
                <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
                  <h3 className="text-lg font-bold text-gray-800">Extracted Education</h3>
                </div>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200 text-left text-sm">
                    <thead className="bg-gray-100 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                      <tr>
                        <th className="px-6 py-3">Degree & Course Details</th>
                        <th className="px-6 py-3">Institution</th>
                        <th className="px-6 py-3">Completion</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200 bg-white">
                      {data.education.map((edu, i) => (
                        <tr key={i} className="hover:bg-gray-50 transition-colors">
                          <td className="px-6 py-4 font-semibold text-gray-900 text-xs">{edu.degree}</td>
                          <td className="px-6 py-4 text-gray-600 font-medium text-xs">{edu.institution}</td>
                          <td className="px-6 py-4 text-gray-500 font-medium text-xs">{edu.year}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

            </div>
          </div>
        )}
      </div>
    </div>
  );
}