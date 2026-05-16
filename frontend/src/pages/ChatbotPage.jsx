import { useState, useEffect, useRef } from 'react';
import { sendMessage, getChatHistory, clearHistory } from '../api/chatbot';
import toast from 'react-hot-toast';
import { Send, Trash2, Bot, User, Loader2 } from 'lucide-react';

export default function ChatbotPage() {
  const [msgs, setMsgs]     = useState([]);
  const [input, setInput]   = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef           = useRef(null);

  useEffect(() => {
    getChatHistory().then(r => {
      const h = r.data?.data || [];
      setMsgs(h.map(m => ({ role: m.role, content: m.content, ts: m.timestamp })));
    }).catch(() => {});
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior:'smooth' });
  }, [msgs]);

  async function handleSend(e) {
    e.preventDefault();
    if (!input.trim()) return;
    const text = input.trim();
    setInput('');
    setMsgs(m => [...m, { role:'user', content:text }]);
    setLoading(true);
    try {
      const res = await sendMessage(text);
      const reply = res.data?.data?.response || 'No response';
      setMsgs(m => [...m, { role:'assistant', content:reply }]);
    } catch (err) {
      toast.error('Could not get response');
      setMsgs(m => [...m, { role:'assistant', content:'Sorry, I encountered an error. Please try again.' }]);
    } finally {
      setLoading(false);
    }
  }

  async function handleClear() {
    await clearHistory().catch(() => {});
    setMsgs([]);
    toast.success('Chat cleared');
  }

  function formatContent(text) {
    // Bold **text** and bullet points
    return text.split('\n').map((line, i) => {
      const formatted = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
      return <p key={i} className="leading-relaxed" dangerouslySetInnerHTML={{ __html: formatted || '&nbsp;' }} />;
    });
  }

  return (
    <div className="flex flex-col h-[calc(100vh-0px)] p-6 animate-in">
      {/* Header */}
      <div className="flex items-center justify-between mb-4 shrink-0">
        <div>
          <h1 className="section-title">AI Financial Chatbot</h1>
          <p className="section-subtitle">Ask anything about loans, EMI, credit scores, budgeting</p>
        </div>
        <button id="clear-chat" onClick={handleClear} className="btn-ghost text-rose-400 hover:text-rose-300">
          <Trash2 size={16} /> Clear
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 pr-1 pb-4">
        {msgs.length === 0 && (
          <div className="flex flex-col items-center justify-center h-48 text-slate-500">
            <Bot size={40} className="mb-3 text-primary-500/50" />
            <p className="text-sm">Hello! Ask me about loans, interest rates, credit scores…</p>
          </div>
        )}
        {msgs.map((msg, i) => {
          const isBot = msg.role === 'assistant';
          return (
            <div key={i} className={`flex gap-3 ${isBot ? '' : 'flex-row-reverse'}`}>
              {/* Avatar */}
              <div className={`w-8 h-8 rounded-full shrink-0 flex items-center justify-center text-white ${
                isBot ? 'bg-gradient-to-br from-primary-500 to-accent-purple' : 'bg-dark-500 border border-dark-400'
              }`}>
                {isBot ? <Bot size={14} /> : <User size={14} />}
              </div>
              {/* Bubble */}
              <div className={`max-w-[75%] px-4 py-3 rounded-2xl text-sm space-y-1 ${
                isBot
                  ? 'bg-dark-700 border border-dark-500 text-slate-200 rounded-tl-none'
                  : 'bg-gradient-to-br from-primary-600 to-primary-700 text-white rounded-tr-none shadow-glow'
              }`}>
                {isBot ? formatContent(msg.content) : <p>{msg.content}</p>}
              </div>
            </div>
          );
        })}
        {loading && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-accent-purple flex items-center justify-center">
              <Bot size={14} className="text-white" />
            </div>
            <div className="bg-dark-700 border border-dark-500 px-4 py-3 rounded-2xl rounded-tl-none">
              <div className="flex gap-1">
                {[0,1,2].map(d => (
                  <div key={d} className="w-2 h-2 bg-primary-400 rounded-full animate-bounce"
                    style={{ animationDelay:`${d*0.15}s` }} />
                ))}
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <form id="chat-form" onSubmit={handleSend} className="flex gap-3 mt-4 shrink-0">
        <input
          id="chat-input"
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="Ask about loan eligibility, EMI, credit scores…"
          disabled={loading}
          className="input-field flex-1"
        />
        <button id="chat-send" type="submit" disabled={loading || !input.trim()} className="btn-primary px-4">
          {loading ? <Loader2 size={18} className="animate-spin" /> : <Send size={18} />}
        </button>
      </form>
    </div>
  );
}
