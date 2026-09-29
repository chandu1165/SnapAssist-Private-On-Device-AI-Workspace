import React, { useState, useEffect, useRef } from 'react';
import {
  Send,
  Bot,
  User,
  FileText,
  Clock,
  Trash2,
  Cpu,
} from 'lucide-react';
import { type DocumentItem, type ChatMessage, type Citation, api } from '../services/api';

interface ChatWorkspaceProps {
  documents: DocumentItem[];
  selectedDocId?: string;
  onSelectDocId: (id?: string) => void;
}

export const ChatWorkspace: React.FC<ChatWorkspaceProps> = ({
  documents,
  selectedDocId,
  onSelectDocId,
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputQuery, setInputQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [activeCitation, setActiveCitation] = useState<Citation | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadChatHistory();
  }, [selectedDocId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const loadChatHistory = async () => {
    try {
      const history = await api.getChatHistory(selectedDocId);
      setMessages(history);
    } catch (err) {
      console.error('Failed to load history', err);
    }
  };

  const handleSendMessage = async (textToSend?: string) => {
    const query = textToSend || inputQuery;
    if (!query.trim() || loading) return;

    setInputQuery('');
    const tempUserMsg: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      message: query,
      created_at: Date.now() / 1000,
    };
    setMessages((prev) => [...prev, tempUserMsg]);
    setLoading(true);

    try {
      const response = await api.sendChat(query, selectedDocId);
      const assistantMsg: ChatMessage = {
        id: response.message_id || Date.now().toString(),
        role: 'assistant',
        message: response.answer,
        citations: response.citations,
        latency_ms: response.latency_ms,
        tokens_used: response.tokens_generated,
        created_at: Date.now() / 1000,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      const errorMsg: ChatMessage = {
        id: Date.now().toString(),
        role: 'assistant',
        message: `Query failed: ${err.message}. Please check if files are indexed.`,
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleClearHistory = async () => {
    if (window.confirm('Clear local conversation history?')) {
      await api.clearChatHistory();
      setMessages([]);
    }
  };

  const samplePrompts = [
    'Summarize this document and identify the three most important action items.',
    'What deadlines or dates are explicitly mentioned?',
    'Explain the Snapdragon Hexagon NPU architecture and TOPS rating.',
    'What are the key conclusions regarding power efficiency?',
  ];

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] max-w-7xl mx-auto space-y-4">
      {/* Top Controls Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 bg-slate-900/60 border border-slate-800 p-3 rounded-2xl">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-red-950/60 border border-red-500/30 text-red-400">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-white flex items-center gap-2">
              Private On-Device AI Chat
              <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-emerald-950/60 border border-emerald-500/30 text-emerald-400">
                Grounded RAG
              </span>
            </h2>
            <p className="text-[11px] text-slate-400">
              Zero cloud transmission • Answers strictly anchored to indexed source chunks
            </p>
          </div>
        </div>

        {/* Filter by Document Selector */}
        <div className="flex items-center gap-2">
          <label className="text-xs text-slate-400 font-medium hidden sm:inline">Context Scope:</label>
          <select
            value={selectedDocId || ''}
            onChange={(e) => onSelectDocId(e.target.value ? e.target.value : undefined)}
            className="text-xs bg-slate-800 text-slate-200 border border-slate-700 rounded-xl px-3 py-1.5 focus:outline-none focus:border-red-500"
          >
            <option value="">All Documents ({documents.length})</option>
            {documents.map((d) => (
              <option key={d.id} value={d.id}>
                {d.filename.length > 25 ? d.filename.slice(0, 25) + '...' : d.filename}
              </option>
            ))}
          </select>
          {messages.length > 0 && (
            <button
              onClick={handleClearHistory}
              title="Clear chat history"
              className="p-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-red-400 transition-colors"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 bg-slate-900/40 border border-slate-800 rounded-3xl p-4 sm:p-6 overflow-y-auto space-y-6">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center max-w-md mx-auto space-y-6">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-red-600/20 to-slate-800 border border-red-500/30 flex items-center justify-center text-red-400">
              <Bot className="w-8 h-8" />
            </div>
            <div className="space-y-2">
              <h3 className="text-lg font-bold text-white">Ask your local knowledge base</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                SnapAssist searches your documents locally, extracts exact matching passages, and synthesizes answers with page citations.
              </p>
            </div>

            {/* Quick Demo Prompts */}
            <div className="w-full space-y-2 text-left">
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 px-1">
                Suggested Demo Questions
              </span>
              <div className="space-y-1.5">
                {samplePrompts.map((p, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSendMessage(p)}
                    className="w-full text-xs text-left p-3 rounded-xl bg-slate-950/70 border border-slate-800 hover:border-red-500/40 text-slate-300 hover:text-white transition-all hover:bg-slate-900/80 flex items-center justify-between group"
                  >
                    <span>{p}</span>
                    <Send className="w-3 h-3 text-slate-500 group-hover:text-red-400 shrink-0 ml-2" />
                  </button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex gap-3 text-xs sm:text-sm ${
                msg.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              {msg.role === 'assistant' && (
                <div className="w-8 h-8 rounded-xl bg-red-600/20 border border-red-500/30 flex items-center justify-center text-red-400 shrink-0 mt-1">
                  <Bot className="w-4 h-4" />
                </div>
              )}
              <div
                className={`max-w-2xl rounded-2xl p-4 sm:p-5 space-y-3 ${
                  msg.role === 'user'
                    ? 'bg-gradient-to-r from-red-600 to-rose-600 text-white rounded-br-sm shadow-md shadow-red-950/40'
                    : 'bg-slate-900/80 border border-slate-800 text-slate-200 rounded-bl-sm shadow-lg'
                }`}
              >
                <div className="whitespace-pre-wrap leading-relaxed font-sans">{msg.message}</div>

                {/* Grounded Citations Drawer */}
                {msg.citations && msg.citations.length > 0 && (
                  <div className="pt-3 border-t border-slate-800/80 space-y-2">
                    <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                      <FileText className="w-3.5 h-3.5 text-red-400" />
                      Source References & Grounding ({msg.citations.length})
                    </span>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                      {msg.citations.map((c, cIdx) => (
                        <div
                          key={cIdx}
                          onClick={() => setActiveCitation(c)}
                          className="p-2.5 rounded-xl bg-slate-950/60 border border-slate-800/90 hover:border-red-500/40 cursor-pointer transition-colors text-xs space-y-1"
                        >
                          <div className="flex items-center justify-between text-slate-300 font-semibold text-[11px]">
                            <span className="truncate max-w-[140px] text-red-300">{c.document_name}</span>
                            <span className="px-1.5 py-0.2 rounded bg-slate-800 text-slate-300 text-[10px]">
                              Page {c.page_number}
                            </span>
                          </div>
                          <p className="text-slate-400 text-[11px] line-clamp-2 italic">"{c.snippet}"</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Latency & Telemetry Pill */}
                {msg.latency_ms !== undefined && msg.latency_ms > 0 && (
                  <div className="flex items-center justify-between pt-2 text-[10px] text-slate-400 border-t border-slate-800/40">
                    <span className="flex items-center gap-1">
                      <Clock className="w-3 h-3 text-slate-400" />
                      Inference: <strong className="text-slate-300">{msg.latency_ms} ms</strong>
                    </span>
                    <span className="flex items-center gap-1 text-slate-400">
                      <Cpu className="w-3 h-3 text-red-400" />
                      <span>Local ONNX / QNN Runtime</span>
                    </span>
                  </div>
                )}
              </div>
              {msg.role === 'user' && (
                <div className="w-8 h-8 rounded-xl bg-slate-800 flex items-center justify-center text-slate-300 shrink-0 mt-1">
                  <User className="w-4 h-4" />
                </div>
              )}
            </div>
          ))
        )}
        {loading && (
          <div className="flex items-center gap-3 text-xs text-slate-400">
            <div className="w-8 h-8 rounded-xl bg-red-600/20 border border-red-500/30 flex items-center justify-center text-red-400">
              <div className="w-4 h-4 border-2 border-red-500 border-t-transparent rounded-full animate-spin"></div>
            </div>
            <span>Synthesizing grounded answer from local chunks...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Box */}
      <div className="relative">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSendMessage();
          }}
          className="flex items-center gap-2 bg-slate-900/80 border border-slate-700/80 rounded-2xl p-2 pl-4 focus-within:border-red-500 focus-within:ring-1 focus-within:ring-red-500 transition-all shadow-xl"
        >
          <input
            type="text"
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            placeholder={
              selectedDocId
                ? 'Ask about selected document...'
                : 'Ask a question across all indexed files...'
            }
            className="flex-1 bg-transparent text-sm text-slate-100 placeholder-slate-500 focus:outline-none"
          />
          <button
            type="submit"
            disabled={!inputQuery.trim() || loading}
            className="px-4 py-2 rounded-xl bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 disabled:opacity-40 disabled:pointer-events-none text-white font-semibold text-xs transition-all shadow-md shadow-red-950/50 flex items-center gap-1.5"
          >
            <span>Ask</span>
            <Send className="w-3.5 h-3.5" />
          </button>
        </form>
      </div>

      {/* Active Citation Modal Drawer */}
      {activeCitation && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-3xl max-w-xl w-full p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="space-y-1">
                <span className="text-xs font-bold text-red-400 uppercase tracking-wider">
                  Verified Local Citation
                </span>
                <h4 className="text-base font-bold text-white">{activeCitation.document_name}</h4>
              </div>
              <span className="px-2.5 py-1 rounded-xl bg-slate-800 text-slate-300 font-semibold text-xs">
                Page {activeCitation.page_number}
              </span>
            </div>
            <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 text-xs text-slate-200 leading-relaxed font-sans">
              "{activeCitation.snippet}"
            </div>
            <div className="flex items-center justify-between text-xs text-slate-400 pt-2">
              <span>Similarity Score: <strong>{(activeCitation.score * 100).toFixed(1)}%</strong></span>
              <button
                onClick={() => setActiveCitation(null)}
                className="px-4 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-medium"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
