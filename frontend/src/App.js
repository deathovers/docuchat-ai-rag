import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Send, Upload, FileText, Trash2 } from 'lucide-react';

const API_BASE = "http://localhost:8000/api/v1";

function App() {
  const [sessionId] = useState(() => {
    const saved = localStorage.getItem('docuchat_session');
    if (saved) return saved;
    const newId = Math.random().toString(36).substring(7);
    localStorage.setItem('docuchat_session', newId);
    return newId;
  });

  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('session_id', sessionId);

    try {
      setLoading(true);
      const res = await axios.post(`${API_BASE}/upload`, formData);
      setFiles([...files, { name: file.name, id: res.data.file_id }]);
    } catch (err) {
      alert("Upload failed: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMsg = { role: 'user', content: input };
    setMessages([...messages, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await axios.post(`${API_BASE}/chat?session_id=${sessionId}&message=${encodeURIComponent(input)}`);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: res.data.answer, 
        sources: res.data.sources 
      }]);
    } catch (err) {
      alert("Chat failed: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  const deleteFile = async (fileId) => {
    try {
      await axios.delete(`${API_BASE}/document/${fileId}?session_id=${sessionId}`);
      setFiles(files.filter(f => f.id !== fileId));
    } catch (err) {
      alert("Delete failed");
    }
  };

  return (
    <div className="flex h-screen bg-gray-100 font-sans">
      {/* Sidebar */}
      <div className="w-64 bg-white border-r p-4 flex flex-col">
        <h1 className="text-xl font-bold mb-6 text-blue-600">DocuChat AI</h1>
        
        <div className="mb-4">
          <label className="flex items-center justify-center w-full p-2 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:border-blue-500 transition-colors">
            <Upload size={20} className="mr-2 text-gray-500" />
            <span className="text-sm text-gray-600">Upload PDF</span>
            <input type="file" className="hidden" onChange={handleUpload} accept=".pdf" />
          </label>
        </div>

        <div className="flex-1 overflow-y-auto">
          <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Documents</h2>
          {files.map(f => (
            <div key={f.id} className="flex items-center justify-between p-2 hover:bg-gray-50 rounded group">
              <div className="flex items-center overflow-hidden">
                <FileText size={16} className="mr-2 text-blue-400 shrink-0" />
                <span className="text-sm truncate text-gray-700">{f.name}</span>
              </div>
              <button onClick={() => deleteFile(f.id)} className="opacity-0 group-hover:opacity-100 text-red-400 hover:text-red-600">
                <Trash2 size={14} />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Main Chat */}
      <div className="flex-1 flex flex-col">
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 && (
            <div className="h-full flex items-center justify-center text-gray-400">
              Upload a document to start chatting
            </div>
          )}
          {messages.map((m, i) => (
            <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] p-4 rounded-2xl ${m.role === 'user' ? 'bg-blue-600 text-white' : 'bg-white border text-gray-800 shadow-sm'}`}>
                <p className="whitespace-pre-wrap">{m.content}</p>
                {m.sources && m.sources.length > 0 && (
                  <div className="mt-3 pt-2 border-t border-gray-100 text-xs text-gray-500">
                    Sources: {m.sources.map(s => `${s.file_name} (p. ${s.page_number})`).join(', ')}
                  </div>
                )}
              </div>
            </div>
          ))}
          {loading && <div className="text-xs text-gray-400 animate-pulse">Processing...</div>}
        </div>

        <div className="p-4 bg-white border-t">
          <div className="max-w-4xl mx-auto flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Ask a question about your documents..."
              className="flex-1 p-3 border rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button 
              onClick={handleSend}
              disabled={loading}
              className="bg-blue-600 text-white p-3 rounded-xl hover:bg-blue-700 disabled:opacity-50"
            >
              <Send size={20} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
