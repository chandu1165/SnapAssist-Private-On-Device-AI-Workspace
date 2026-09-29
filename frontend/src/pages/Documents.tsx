import React, { useState, useRef } from 'react';
import {
  Upload,
  FileText,
  Trash2,
  Sparkles,
  Layers,
  CheckCircle2,
  AlertCircle,
  FileUp,
  X,
  File,
  Calendar,
} from 'lucide-react';
import { type DocumentItem, type ChunkItem, api } from '../services/api';

interface DocumentsProps {
  documents: DocumentItem[];
  onRefresh: () => void;
  onNavigateToChat: (docId: string) => void;
}

export const Documents: React.FC<DocumentsProps> = ({
  documents,
  onRefresh,
  onNavigateToChat,
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);

  // Chunk inspection state
  const [inspectingDoc, setInspectingDoc] = useState<DocumentItem | null>(null);
  const [chunks, setChunks] = useState<ChunkItem[]>([]);
  const [loadingChunks, setLoadingChunks] = useState(false);

  // Summary inspection state
  const [summaryDoc, setSummaryDoc] = useState<DocumentItem | null>(null);
  const [generatingSummary, setGeneratingSummary] = useState(false);
  const [summaryData, setSummaryData] = useState<any>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = async (file: File) => {
    setUploading(true);
    setUploadError(null);
    setUploadSuccess(null);
    try {
      const res = await api.uploadDocument(file);
      setUploadSuccess(`Successfully parsed & indexed '${file.name}' (${res.chunk_count} chunks created locally).`);
      onRefresh();
    } catch (err: any) {
      setUploadError(err.message || 'File upload failed');
    } finally {
      setUploading(false);
      setTimeout(() => setUploadSuccess(null), 5000);
    }
  };

  const onDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const onDragLeave = () => {
    setIsDragging(false);
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  const handleDelete = async (docId: string, filename: string) => {
    if (window.confirm(`Delete '${filename}' and remove all stored chunks?`)) {
      try {
        await api.deleteDocument(docId);
        onRefresh();
      } catch (err: any) {
        alert(`Failed to delete: ${err.message}`);
      }
    }
  };

  const handleInspectChunks = async (doc: DocumentItem) => {
    setInspectingDoc(doc);
    setLoadingChunks(true);
    try {
      const data = await api.getDocumentChunks(doc.id);
      setChunks(data);
    } catch (err: any) {
      alert(`Could not load chunks: ${err.message}`);
    } finally {
      setLoadingChunks(false);
    }
  };

  const handleViewSummary = async (doc: DocumentItem) => {
    setSummaryDoc(doc);
    if (doc.summary) {
      setSummaryData(doc.summary);
      return;
    }
    setGeneratingSummary(true);
    try {
      const res = await api.summarize(doc.id, 'comprehensive');
      setSummaryData(res.summary);
      onRefresh();
    } catch (err: any) {
      alert(`Failed to generate summary: ${err.message}`);
    } finally {
      setGeneratingSummary(false);
    }
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white tracking-tight">Document Repository</h2>
          <p className="text-xs text-slate-400 mt-1">
            Import PDFs, DOCX, TXT, Markdown, or images. All parsing, chunking, and embeddings occur 100% locally.
          </p>
        </div>
        <button
          onClick={() => fileInputRef.current?.click()}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-red-600 hover:bg-red-500 text-white font-semibold text-xs transition-all shadow-md shadow-red-950/40"
        >
          <FileUp className="w-4 h-4" />
          Choose File to Upload
        </button>
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          accept=".pdf,.docx,.txt,.md,.png,.jpg,.jpeg,.webp"
          onChange={(e) => {
            if (e.target.files && e.target.files[0]) {
              handleFileUpload(e.target.files[0]);
            }
          }}
        />
      </div>

      {/* Drag & Drop Upload Zone */}
      <div
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onDrop={onDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-3xl p-8 sm:p-12 text-center cursor-pointer transition-all ${
          isDragging
            ? 'border-red-500 bg-red-950/20 scale-[0.99]'
            : 'border-slate-800 hover:border-slate-700 bg-slate-900/40'
        }`}
      >
        <div className="max-w-md mx-auto space-y-3">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-red-600/20 to-slate-800 flex items-center justify-center mx-auto text-red-400 border border-red-500/20">
            {uploading ? (
              <div className="w-6 h-6 border-2 border-red-500 border-t-transparent rounded-full animate-spin"></div>
            ) : (
              <Upload className="w-6 h-6" />
            )}
          </div>
          <div className="space-y-1">
            <p className="text-sm font-semibold text-slate-200">
              {uploading ? 'Parsing and indexing document locally...' : 'Drop files here or click to browse'}
            </p>
            <p className="text-xs text-slate-400">
              Supports PDF, DOCX, TXT, Markdown, PNG, and JPG. Zero bytes sent to cloud.
            </p>
          </div>
        </div>
      </div>

      {/* Feedback alerts */}
      {uploadSuccess && (
        <div className="p-4 rounded-2xl bg-emerald-950/60 border border-emerald-500/30 text-emerald-300 text-xs flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>{uploadSuccess}</span>
        </div>
      )}
      {uploadError && (
        <div className="p-4 rounded-2xl bg-red-950/60 border border-red-500/30 text-red-300 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
          <span>{uploadError}</span>
        </div>
      )}

      {/* Documents Table */}
      <div className="rounded-3xl bg-slate-900/50 border border-slate-800 overflow-hidden">
        <div className="p-5 border-b border-slate-800 flex items-center justify-between">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
            Indexed Documents ({documents.length})
          </span>
          <span className="text-xs text-slate-400">Local SQLite & FAISS-style Vector Index</span>
        </div>

        {documents.length === 0 ? (
          <div className="p-12 text-center space-y-2">
            <File className="w-10 h-10 text-slate-600 mx-auto" />
            <p className="text-sm text-slate-400">No documents in your local workspace.</p>
            <p className="text-xs text-slate-400">Upload a PDF or document above to begin local RAG querying.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider font-semibold">
                  <th className="py-3 px-5">Document Name</th>
                  <th className="py-3 px-4">Type</th>
                  <th className="py-3 px-4">Size</th>
                  <th className="py-3 px-4">Pages</th>
                  <th className="py-3 px-4">Chunks</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {documents.map((doc) => (
                  <tr key={doc.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="py-4 px-5 font-semibold text-slate-200">
                      <div className="flex items-center gap-3">
                        <div className="p-2 rounded-xl bg-slate-800 text-red-400">
                          <FileText className="w-4 h-4" />
                        </div>
                        <div>
                          <div className="font-medium text-slate-200 truncate max-w-xs">{doc.filename}</div>
                          <div className="text-[10px] text-slate-400">ID: {doc.id.slice(0, 8)}...</div>
                        </div>
                      </div>
                    </td>
                    <td className="py-4 px-4 font-mono uppercase text-slate-400">{doc.file_type}</td>
                    <td className="py-4 px-4 text-slate-400">{(doc.file_size / 1024).toFixed(1)} KB</td>
                    <td className="py-4 px-4 text-slate-300 font-semibold">{doc.page_count}</td>
                    <td className="py-4 px-4 text-slate-300 font-semibold">{doc.chunk_count}</td>
                    <td className="py-4 px-4">
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-950/60 border border-emerald-500/30 text-emerald-400 font-semibold text-[10px]">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                        {doc.status}
                      </span>
                    </td>
                    <td className="py-4 px-5 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => handleViewSummary(doc)}
                          title="Generate/View Summary"
                          className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors"
                        >
                          <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                        </button>
                        <button
                          onClick={() => handleInspectChunks(doc)}
                          title="Inspect Chunks"
                          className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors"
                        >
                          <Layers className="w-3.5 h-3.5 text-blue-400" />
                        </button>
                        <button
                          onClick={() => onNavigateToChat(doc.id)}
                          className="px-2.5 py-1 rounded-lg bg-red-600/20 hover:bg-red-600/30 border border-red-500/40 text-red-300 text-xs font-semibold transition-colors"
                        >
                          Chat
                        </button>
                        <button
                          onClick={() => handleDelete(doc.id, doc.filename)}
                          title="Delete Document"
                          className="p-1.5 rounded-lg bg-slate-800/80 hover:bg-red-950/60 text-slate-400 hover:text-red-400 transition-colors"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Chunk Inspector Modal */}
      {inspectingDoc && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-3xl max-w-3xl w-full max-h-[85vh] flex flex-col shadow-2xl">
            <div className="p-5 border-b border-slate-800 flex items-center justify-between">
              <div>
                <h3 className="font-bold text-white text-base flex items-center gap-2">
                  <Layers className="w-4 h-4 text-blue-400" />
                  Chunk Inspector: {inspectingDoc.filename}
                </h3>
                <p className="text-xs text-slate-400">
                  {chunks.length} semantic chunks with vector embeddings stored locally.
                </p>
              </div>
              <button
                onClick={() => setInspectingDoc(null)}
                className="p-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="p-6 overflow-y-auto space-y-4 text-xs">
              {loadingChunks ? (
                <div className="text-center py-10 text-slate-400">Loading chunk representations...</div>
              ) : chunks.length === 0 ? (
                <div className="text-center py-10 text-slate-400">No chunks found for this document.</div>
              ) : (
                chunks.map((c) => (
                  <div key={c.id} className="p-4 rounded-2xl bg-slate-950/70 border border-slate-800 space-y-2">
                    <div className="flex items-center justify-between text-slate-400 font-semibold text-[11px]">
                      <span className="text-red-400">Chunk #{c.chunk_index + 1}</span>
                      <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                        Page {c.page_number}
                      </span>
                      <span>~{c.token_count} tokens</span>
                    </div>
                    <p className="text-slate-300 leading-relaxed font-sans">{c.content}</p>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}

      {/* Document Summary Modal */}
      {summaryDoc && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-3xl max-w-3xl w-full max-h-[85vh] flex flex-col shadow-2xl">
            <div className="p-5 border-b border-slate-800 flex items-center justify-between">
              <div>
                <h3 className="font-bold text-white text-base flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-amber-400" />
                  Local AI Summary: {summaryDoc.filename}
                </h3>
                <p className="text-xs text-slate-400">
                  Extracted entirely on-device with zero remote API calls.
                </p>
              </div>
              <button
                onClick={() => {
                  setSummaryDoc(null);
                  setSummaryData(null);
                }}
                className="p-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="p-6 overflow-y-auto space-y-6 text-xs">
              {generatingSummary ? (
                <div className="text-center py-12 space-y-3">
                  <div className="w-8 h-8 border-2 border-red-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
                  <p className="text-slate-400">Synthesizing document structure locally...</p>
                </div>
              ) : summaryData ? (
                <>
                  {/* TL;DR */}
                  <div className="p-4 rounded-2xl bg-red-950/20 border border-red-500/30 space-y-2">
                    <span className="font-bold text-red-400 uppercase tracking-wider text-[11px]">
                      TL;DR Executive Summary
                    </span>
                    <p className="text-slate-200 text-sm leading-relaxed font-medium">
                      {summaryData.tldr}
                    </p>
                  </div>

                  {/* Key Points */}
                  {summaryData.key_points && summaryData.key_points.length > 0 && (
                    <div className="space-y-2">
                      <span className="font-bold text-slate-300 uppercase tracking-wider text-[11px]">
                        Key Points & Conclusions
                      </span>
                      <ul className="space-y-1.5">
                        {summaryData.key_points.map((pt: string, idx: number) => (
                          <li key={idx} className="p-3 rounded-xl bg-slate-950/60 border border-slate-800 text-slate-300 flex items-start gap-2">
                            <span className="text-red-400 font-bold">•</span>
                            <span>{pt}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Action Items */}
                  {summaryData.action_items && summaryData.action_items.length > 0 && (
                    <div className="space-y-2">
                      <span className="font-bold text-amber-400 uppercase tracking-wider text-[11px] flex items-center gap-1.5">
                        <CheckCircle2 className="w-3.5 h-3.5" /> Action Items & Tasks
                      </span>
                      <ul className="space-y-1.5">
                        {summaryData.action_items.map((act: string, idx: number) => (
                          <li key={idx} className="p-3 rounded-xl bg-amber-950/20 border border-amber-500/30 text-amber-200 flex items-start gap-2">
                            <span className="font-bold text-amber-400">✓</span>
                            <span>{act}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Important Dates */}
                  {summaryData.important_dates && summaryData.important_dates.length > 0 && (
                    <div className="space-y-2">
                      <span className="font-bold text-indigo-400 uppercase tracking-wider text-[11px] flex items-center gap-1.5">
                        <Calendar className="w-3.5 h-3.5" /> Deadlines & Dates
                      </span>
                      <div className="flex flex-wrap gap-2">
                        {summaryData.important_dates.map((dt: string, idx: number) => (
                          <span key={idx} className="px-3 py-1 rounded-xl bg-indigo-950/50 border border-indigo-500/30 text-indigo-300 font-medium">
                            {dt}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Topics / Entities */}
                  {summaryData.entities_topics && summaryData.entities_topics.length > 0 && (
                    <div className="space-y-2">
                      <span className="font-bold text-slate-400 uppercase tracking-wider text-[11px]">
                        Identified Entities & Topics
                      </span>
                      <div className="flex flex-wrap gap-1.5">
                        {summaryData.entities_topics.map((entity: string, idx: number) => (
                          <span key={idx} className="px-2.5 py-0.5 rounded-lg bg-slate-800 text-slate-300 text-[11px]">
                            #{entity}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </>
              ) : null}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
