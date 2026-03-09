import React, { useState, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';

export default function DocuChat() {
  const [sessionId] = useState(uuidv4());
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [files, setFiles] = useState([]);

  const handleUpload = async (e) => {
    const uploadedFiles = Array.from(e.target.files);
    if (uploadedFiles.length > 10) {
      alert("Max 10 files allowed");
      return;
    }

    const formData = new FormData();
    uploadedFiles.forEach(file => formData.append('files', file));

    try {
      setLoading(true);
      const res = await fetch(`http://localhost:8000/api/v1/upload?session_id=${sessionId}`, {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      setFiles(uploadedFiles.map(f => f.name));
      alert("Files uploaded and indexed!");
    } catch (err) {
      console.error(err);
      alert("Upload failed");
    } finally {
      setLoading(false);
    }
  };

  const handleChat = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    const userMsg = { role: 'user', content: query };
    setMessages(prev => [...prev, userMsg]);
    setQuery('');
    setLoading(true);

    try {
      const history = messages.map(m => ({ role: m.role, content: m.content }));
      const res = await fetch('http://localhost:8000/api/v1/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query,
          session_id: sessionId,
          history: history.slice(-5)
        }),
      });
      const data = await res.json();
      setMessages(prev => [...prev, { role: 'assistant', content: data.answer, sources: data.sources }]);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">DocuChat AI</h1>
      
      <div className="mb-8 p-4 border rounded bg-gray-50">
        <h2 className="text-xl font-semibold mb-2">1. Upload PDFs (Max 10)</h2>
        <input type="file" multiple accept=".pdf" onChange={handleUpload} className="mb-2" />
        {files.length > 0 && (
          <div className="text-sm text-gray-600">
            Uploaded: {files.join(', ')}
          </div>
        )}
      </div>

      <div className="mb-8 h-96 overflow-y-auto border p-4 rounded bg-white">
        {messages.map((msg, i) => (
          <div key={i} className={`mb-4 ${msg.role === 'user' ? 'text-right' : 'text-left'}`}>
            <div className={`inline-block p-3 rounded-lg ${msg.role === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-black'}`}>
              {msg.content}
              {msg.sources && msg.sources.length > 0 && (
                <div className="mt-2 pt-2 border-t border-gray-400 text-xs italic">
                  Sources: {msg.sources.map(s => `${s.document_name} (p. ${s.page_number})`).join(', ')}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && <div className="text-center text-gray-500 italic">Processing...</div>}
      </div>

      <form onSubmit={handleChat} className="flex gap-2">
        <input 
          type="text" 
          value={query} 
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask a question about your documents..."
          className="flex-1 p-2 border rounded"
        />
        <button type="submit" disabled={loading} className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 disabled:bg-gray-400">
          Send
        </button>
      </form>
    </div>
  );
}
