import React, { useState } from 'react';
import { Search as SearchIcon, FileText, ArrowRight, Zap, Layers } from 'lucide-react';
import { api } from '../services/api';

interface SearchProps {
  onNavigateToChat: (docId: string) => void;
}

export const Search: React.FC<SearchProps> = ({ onNavigateToChat }) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [latency, setLatency] = useState<number | null>(null);
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!query.trim() || loading) return;

    setLoading(true);
    setHasSearched(true);
    try {
      const data = await api.semanticSearch(query.trim(), undefined, 8);
      setResults(data.results || []);
      setLatency(data.search_latency_ms);
    } catch (err: any) {
      alert(`Search failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const sampleSearches = [
    'battery optimization and power draw',
    'qualcomm hexagon npu tops',
    'action items and submission deadline',
    'onnx runtime qnn execution provider',
  ];

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div>
        <h2 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
          <SearchIcon className="w-6 h-6 text-red-500" />
          Semantic Vector Search
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Perform high-dimensional cosine similarity searches across your local files. Finds concepts, not just exact keywords.
        </p>
      </div>

      {/* Search Bar */}
      <form onSubmit={handleSearch} className="relative">
        <div className="flex items-center gap-2 bg-slate-900/80 border border-slate-700/80 rounded-2xl p-2 pl-4 focus-within:border-red-500 focus-within:ring-1 focus-within:ring-red-500 transition-all shadow-xl">
          <SearchIcon className="w-5 h-5 text-slate-400 shrink-0" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Type a natural language query (e.g., 'Find documents discussing battery efficiency')..."
            className="flex-1 bg-transparent text-sm text-slate-100 placeholder-slate-500 focus:outline-none"
          />
          <button
            type="submit"
            disabled={!query.trim() || loading}
            className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 disabled:opacity-40 text-white font-semibold text-xs transition-all shadow-md shadow-red-950/40"
          >
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>
      </form>

      {/* Suggested Queries */}
      <div className="flex flex-wrap items-center gap-2 text-xs">
        <span className="text-slate-500 font-medium">Try searching:</span>
        {sampleSearches.map((s, idx) => (
          <button
            key={idx}
            onClick={() => {
              setQuery(s);
              setTimeout(() => {
                api.semanticSearch(s, undefined, 8).then((res) => {
                  setResults(res.results || []);
                  setLatency(res.search_latency_ms);
                  setHasSearched(true);
                });
              }, 50);
            }}
            className="px-3 py-1 rounded-xl bg-slate-800/80 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-700 transition-colors"
          >
            "{s}"
          </button>
        ))}
      </div>

      {/* Results Header */}
      {hasSearched && (
        <div className="flex items-center justify-between text-xs text-slate-400 pt-2 border-t border-slate-800">
          <span>Found {results.length} matching passages</span>
          {latency !== null && (
            <span className="flex items-center gap-1 text-emerald-400 font-semibold">
              <Zap className="w-3.5 h-3.5" /> Vector search completed in {latency} ms (SIMD Cosine Dot-Product)
            </span>
          )}
        </div>
      )}

      {/* Results List */}
      <div className="space-y-3">
        {loading ? (
          <div className="text-center py-16 space-y-3">
            <div className="w-8 h-8 border-2 border-red-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
            <p className="text-xs text-slate-400">Computing dense vector similarities locally...</p>
          </div>
        ) : results.length === 0 && hasSearched ? (
          <div className="text-center py-16 bg-slate-900/30 border border-slate-800 rounded-3xl space-y-2">
            <Layers className="w-8 h-8 text-slate-600 mx-auto" />
            <p className="text-sm text-slate-300 font-medium">No matching passages found.</p>
            <p className="text-xs text-slate-400">Try rephrasing your search or indexing additional documents.</p>
          </div>
        ) : (
          results.map((res, idx) => (
            <div
              key={idx}
              className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 hover:border-red-500/30 transition-all space-y-3 shadow-md"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-xs font-semibold text-slate-200">
                  <FileText className="w-4 h-4 text-red-400" />
                  <span>{res.document_name}</span>
                  <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 text-[10px]">
                    Page {res.page_number}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="px-2.5 py-0.5 rounded-full bg-red-950/60 border border-red-500/30 text-red-400 text-[10px] font-bold">
                    {(res.score * 100).toFixed(1)}% match
                  </span>
                  <button
                    onClick={() => onNavigateToChat(res.doc_id)}
                    className="p-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white"
                    title="Open in Chat Workspace"
                  >
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed font-sans bg-slate-950/40 p-3 rounded-xl border border-slate-800/50">
                "{res.content}"
              </p>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
