// API Client for SnapAssist On-Device Workspace

export interface DocumentItem {
  id: string;
  filename: string;
  file_type: string;
  file_size: number;
  page_count: number;
  chunk_count: number;
  status: string;
  summary?: any;
  created_at: number;
}

export interface ChunkItem {
  id: string;
  chunk_index: number;
  page_number: number;
  content: string;
  token_count: number;
}

export interface Citation {
  document_name: string;
  page_number: number;
  snippet: string;
  score: number;
}

export interface ChatMessage {
  id: string;
  session_id?: string;
  doc_id?: string;
  role: 'user' | 'assistant';
  message: string;
  citations?: Citation[];
  latency_ms?: number;
  tokens_used?: number;
  created_at?: number;
}

export interface PrivacyMetrics {
  local_processing: string;
  documents_uploaded_to_cloud: number;
  ai_api_calls: number;
  network_egress_bytes: number;
  indexed_documents_count: number;
  indexed_chunks_count: number;
  total_queries_executed: number;
  offline_mode: string;
  privacy_guarantee: string;
  audit_events: Array<{
    action: string;
    target: string;
    is_local: boolean;
    bytes_outbound: number;
    external_api_calls: number;
    timestamp: number;
    details: string;
  }>;
}

export interface PerformanceMetrics {
  hardware: {
    platform: {
      os: string;
      architecture: string;
      processor: string;
      is_arm64: boolean;
      is_snapdragon_device: boolean;
      target_device_profile: string;
    };
    npu_telemetry: {
      npu_name: string;
      rated_tops_design_target: number;
      npu_status: string;
      execution_provider: string;
      accelerator: string;
      status: string;
      reason: string;
      active_execution_provider: string;
      acceleration_type: string;
      is_hardware_npu_active: boolean;
      available_ort_providers: string[];
      qualcomm_ai_hub_installed: boolean;
      qualcomm_ai_hub_version: string | null;
    };
    system_resources: {
      total_memory_gb: number;
      available_memory_gb: number;
      memory_used_percent: number;
      cpu_cores: number;
      cpu_frequency_mhz: string | number;
    };
  };
  active_model: string;
  active_backend: string;
  execution_provider: string;
  average_rag_latency_ms: number;
  average_ingest_latency_ms: number;
  average_throughput_tokens_sec: number;
  process_memory_rss_mb: number;
  telemetry: Array<{
    operation: string;
    model: string;
    backend: string;
    execution_provider: string;
    latency_ms: number;
    throughput_tokens_sec: number;
    memory_mb: number;
    timestamp: number;
  }>;
}

export interface WorkspaceStats {
  total_documents: number;
  total_chunks: number;
  total_queries: number;
  average_latency_ms: number;
  privacy_score_percent: number;
  cloud_transfers: number;
  offline_ready: boolean;
}

const API_BASE = '/api';

export const api = {
  // Documents
  async listDocuments(): Promise<DocumentItem[]> {
    const res = await fetch(`${API_BASE}/documents`);
    if (!res.ok) throw new Error('Failed to fetch documents');
    return res.json();
  },

  async getDocument(docId: string): Promise<DocumentItem> {
    const res = await fetch(`${API_BASE}/documents/${docId}`);
    if (!res.ok) throw new Error('Failed to fetch document details');
    return res.json();
  },

  async getDocumentChunks(docId: string): Promise<ChunkItem[]> {
    const res = await fetch(`${API_BASE}/documents/${docId}/chunks`);
    if (!res.ok) throw new Error('Failed to fetch document chunks');
    return res.json();
  },

  async uploadDocument(file: File): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/documents/upload`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Upload failed' }));
      throw new Error(err.detail || 'Upload failed');
    }
    return res.json();
  },

  async deleteDocument(docId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/documents/${docId}`, {
      method: 'DELETE',
    });
    if (!res.ok) throw new Error('Failed to delete document');
    return res.json();
  },

  // Chat & RAG
  async sendChat(query: string, docId?: string, topK: number = 4): Promise<any> {
    const res = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, doc_id: docId || null, top_k: topK }),
    });
    if (!res.ok) throw new Error('Chat query failed');
    return res.json();
  },

  async getChatHistory(docId?: string): Promise<ChatMessage[]> {
    const url = docId ? `${API_BASE}/chat/history?doc_id=${docId}` : `${API_BASE}/chat/history`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch chat history');
    return res.json();
  },

  async clearChatHistory(): Promise<any> {
    const res = await fetch(`${API_BASE}/chat/history`, {
      method: 'DELETE',
    });
    if (!res.ok) throw new Error('Failed to clear chat history');
    return res.json();
  },

  // Summarize
  async summarize(docId: string, summaryType: string = 'comprehensive'): Promise<any> {
    const res = await fetch(`${API_BASE}/summarize/${docId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ summary_type: summaryType }),
    });
    if (!res.ok) throw new Error('Summarization failed');
    return res.json();
  },

  // Search
  async semanticSearch(query: string, docId?: string, topK: number = 6): Promise<any> {
    const res = await fetch(`${API_BASE}/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, doc_id: docId || null, top_k: topK }),
    });
    if (!res.ok) throw new Error('Semantic search failed');
    return res.json();
  },

  // Image Analysis
  async analyzeImage(file: File): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/image/analyze`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) throw new Error('Image analysis failed');
    return res.json();
  },

  async imageQA(query: string, ocrText: string, visualType: string): Promise<any> {
    const res = await fetch(`${API_BASE}/image/qa`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, ocr_text: ocrText, visual_type: visualType }),
    });
    if (!res.ok) throw new Error('Image QA failed');
    return res.json();
  },

  // System
  async getPrivacyMetrics(): Promise<PrivacyMetrics> {
    const res = await fetch(`${API_BASE}/system/privacy`);
    if (!res.ok) throw new Error('Failed to fetch privacy metrics');
    return res.json();
  },

  async getPerformanceMetrics(): Promise<PerformanceMetrics> {
    const res = await fetch(`${API_BASE}/system/performance`);
    if (!res.ok) throw new Error('Failed to fetch performance metrics');
    return res.json();
  },

  async getStats(): Promise<WorkspaceStats> {
    const res = await fetch(`${API_BASE}/system/stats`);
    if (!res.ok) throw new Error('Failed to fetch stats');
    return res.json();
  },

  async listProviders(): Promise<any> {
    const res = await fetch(`${API_BASE}/system/providers`);
    if (!res.ok) throw new Error('Failed to fetch providers');
    return res.json();
  },

  async switchProvider(providerKey: string): Promise<any> {
    const res = await fetch(`${API_BASE}/system/provider`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ provider_key: providerKey }),
    });
    if (!res.ok) throw new Error('Failed to switch provider');
    return res.json();
  },
};
