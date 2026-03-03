"use client";

import { useState, useEffect, useRef } from 'react';
import { Send, FileText, Trash2, Upload, Loader2 } from 'lucide-react';

export default function ChatPage() {
  const [sessionId, setSessionId] = useState('');
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    let id = localStorage.getItem('docuchat_session');
    if (!id) {
      id = Math.random().toString(36).substring(7);
      localStorage.setItem('docuchat_session', id);
    }
    setSessionId(id);
    fetchFiles(id);
  }, []);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const fetchFiles = async (id) => {
    try {
      const res = await fetch(`http://localhost:8000/files/${id}`);
      const data = await res.json();
      setFiles(data.files || []);
    } catch (e) { console.error(e); }
  };

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('session_id', sessionId);

    try {
      await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData,
      });
      fetchFiles(sessionId);
    } catch (e) {
      alert("Upload failed");
    } finally {
      setUploading(false);
    }
  };

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMsg = { role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    const assistantMsg = { role: 'assistant', content: '', sources: [] };
    setMessages(prev => [...prev, assistantMsg]);

    try {
      const response = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, question: input }),
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let fullContent = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6));
            if (data.content) {
              fullContent += data.content;
              setMessages(prev => {
                const last = [...prev];
                last[last.length - 1].content = fullContent;
                return last;
              });
            }
            if (data.sources) {
              setMessages(prev => {
                const last = [...prev];
                last[last.length - 1].sources = data.sources;
                return last;
              });
            }
          }
        }
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const clearSession = async () => {
    await fetch(`http://localhost:8000/session/${sessionId}`, { method: 'DELETE' });
    setMessages([]);
    setFiles([]);
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="w-64 bg-white border-r flex flex-col">
        <div className="p-4 border-b font-bold text-xl flex items-center gap-2">
          <FileText className="text-blue-600" /> DocuChat AI
        </div>
        <div className="p-4 flex-1 overflow-y-auto">
          <div className="text-xs font-semibold text-gray-500 uppercase mb-4">Documents</div>
          {files.map((f, i) => (
            <div key={i} className="flex items-center gap-2 p-2 text-sm text-gray-700 bg-gray-100 rounded mb-2 truncate">
              <FileText size={14} /> {f}
            </div>
          ))}
          <label className="mt-4 flex items-center justify-center gap-2 p-2 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:border-blue-500 transition-colors">
            {uploading ? <Loader2 className="animate-spin" size={18} /> : <Upload size={18} />}
            <span className="text-sm font-medium">{uploading ? 'Uploading...' : 'Upload PDF'}</span>
            <input type="file" className="hidden" accept=".pdf" onChange={handleUpload} disabled={uploading} />
          </label>
        </div>
        <div className="p-4 border-t">
          <button onClick={clearSession} className="flex items-center gap-2 text-red-500 text-sm hover:bg-red-50 p-2 rounded w-full">
            <Trash2 size={16} /> Clear Session
          </button>
        </div>
      </div>

      {/* Main Chat */}
      <div className="flex-1 flex flex-col">
        <div ref={scrollRef} className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 && (
            <div className="h-full flex flex-col items-center justify-center text-gray-400">
              <FileText size={48} className="mb-4 opacity-20" />
              <p>Upload a PDF and ask a question to get started.</p>
            </div>
          )}
          {messages.map((m, i) => (
            <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] p-4 rounded-2xl ${m.role === 'user' ? 'bg-blue-600 text-white' : 'bg-white border shadow-sm'}`}>
                <div className="whitespace-pre-wrap">{m.content}</div>
                {m.sources?.length > 0 && (
                  <div className="mt-3 pt-3 border-t text-xs text-gray-500">
                    <div className="font-semibold mb-1">Sources:</div>
                    <div className="flex flex-wrap gap-2">
                      {m.sources.map((s, si) => (
                        <span key={si} className="bg-gray-100 px-2 py-1 rounded">
                          {s.file_name} (Pg {s.page})
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
          {loading && messages[messages.length-1]?.role === 'user' && (
             <div className="flex justify-start">
               <div className="bg-white border p-4 rounded-2xl shadow-sm">
                 <Loader2 className="animate-spin text-blue-600" />
               </div>
             </div>
          )}
        </div>

        {/* Input */}
        <div className="p-6 bg-white border-t">
          <div className="max-w-4xl mx-auto flex gap-4">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Ask a question about your documents..."
              className="flex-1 p-3 border rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={handleSend}
              disabled={loading || !input.trim()}
              className="bg-blue-600 text-white p-3 rounded-xl hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              <Send size={20} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
