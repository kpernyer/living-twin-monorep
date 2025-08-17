import React, { useState } from 'react';
import { apiFetch } from '../../shared/api';
import { useAuth } from '../auth/AuthProvider';

const DocumentInjection = () => {
  const { getTenantId } = useAuth();
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadTitle, setUploadTitle] = useState('');

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    setSelectedFile(file);
    if (file && !uploadTitle) {
      setUploadTitle(file.name.replace(/\.[^/.]+$/, '')); // Remove extension for title
    }
  };

  const doFileUpload = async () => {
    if (!selectedFile) {
      alert('Please select a file first');
      return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('title', uploadTitle || selectedFile.name);
    formData.append('tenantId', getTenantId());

    try {
      const resp = await apiFetch('/query/ingest/upload', {
        method: 'POST',
        body: formData,
      });
      const data = await resp.json();

      if (resp.ok) {
        alert(`File uploaded successfully!\nType: ${data.fileType}\nChunks: ${data.chunks}`);
        setSelectedFile(null);
        setUploadTitle('');
        // Reset file input
        const fileInput = document.getElementById('fileInput');
        if (fileInput) fileInput.value = '';
      } else {
        alert(`Upload failed: ${data.detail || 'Unknown error'}`);
      }
    } catch (error) {
      alert(`Upload failed: ${error.message}`);
    }
  };

  return (
    <div className="bg-white overflow-hidden shadow rounded-lg">
      <div className="px-4 py-5 sm:p-6">
        <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">Upload Documents (PDF, DOCX, TXT)</h3>
        <div className="space-y-4">
          <input
            value={uploadTitle}
            onChange={(e) => setUploadTitle(e.target.value)}
            placeholder="Document title (optional)"
            className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
          />
          <input
            id="fileInput"
            type="file"
            accept=".pdf,.docx,.doc,.txt,.md"
            onChange={handleFileSelect}
            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
          />
          {selectedFile && (
            <div className="p-3 bg-gray-50 rounded-md">
              Selected: <strong>{selectedFile.name}</strong> ({(selectedFile.size / 1024).toFixed(1)} KB)
            </div>
          )}
          <button
            onClick={doFileUpload}
            disabled={!selectedFile}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-md text-sm font-medium"
          >
            Upload Document
          </button>
        </div>
      </div>
    </div>
  );
};

export default DocumentInjection;
