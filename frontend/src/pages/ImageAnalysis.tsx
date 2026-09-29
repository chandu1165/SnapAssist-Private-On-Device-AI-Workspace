import React, { useState, useRef } from 'react';
import {
  ScanEye,
  Image as ImageIcon,
  MessageSquare,
  Send,
  Eye,
  Layout,
} from 'lucide-react';
import { api } from '../services/api';

export const ImageAnalysis: React.FC = () => {
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  const [imagePreviewUrl, setImagePreviewUrl] = useState<string | null>(null);
  const [qaQuery, setQaQuery] = useState('');
  const [qaAnswer, setQaAnswer] = useState<string | null>(null);
  const [qaLoading, setQaLoading] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleImageFile = async (file: File) => {
    setAnalyzing(true);
    setAnalysisResult(null);
    setQaAnswer(null);
    setImagePreviewUrl(URL.createObjectURL(file));

    try {
      const data = await api.analyzeImage(file);
      setAnalysisResult(data);
    } catch (err: any) {
      alert(`Image analysis failed: ${err.message}`);
    } finally {
      setAnalyzing(false);
    }
  };

  const handleLoadSampleScreenshot = async () => {
    setAnalyzing(true);
    setAnalysisResult(null);
    setQaAnswer(null);
    try {
      const canvas = document.createElement('canvas');
      canvas.width = 900;
      canvas.height = 450;
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.fillStyle = '#0f172a';
        ctx.fillRect(0, 0, 900, 450);
        ctx.fillStyle = '#1e293b';
        ctx.fillRect(40, 30, 820, 60);
        ctx.fillStyle = '#f8fafc';
        ctx.font = 'bold 20px sans-serif';
        ctx.fillText('Snapdragon X Elite Copilot+ Telemetry Monitor', 60, 68);

        ctx.fillStyle = '#ef4444';
        ctx.font = '16px monospace';
        ctx.fillText('NPU: Hexagon 45 TOPS [ONLINE]', 60, 150);
        ctx.fillStyle = '#38bdf8';
        ctx.fillText('Provider: QNNExecutionProvider / DirectML', 60, 190);
        ctx.fillStyle = '#22c55e';
        ctx.fillText('Privacy: 100% On-Device / Cloud Egress: 0 Bytes', 60, 230);
        ctx.fillStyle = '#cbd5e1';
        ctx.fillText('Model: Llama-3.2-1B-Instruct (W4A16 Quantized)', 60, 270);
        ctx.fillText('Deadline: October 15, 2026 Qualcomm AI Lab Challenge', 60, 310);
      }
      canvas.toBlob(async (blob) => {
        if (blob) {
          const file = new File([blob], 'system_telemetry_screenshot.png', { type: 'image/png' });
          setImagePreviewUrl(URL.createObjectURL(file));
          const data = await api.analyzeImage(file);
          setAnalysisResult(data);
          setAnalyzing(false);
        }
      }, 'image/png');
    } catch (err: any) {
      alert(`Error loading sample: ${err.message}`);
      setAnalyzing(false);
    }
  };

  const handleImageQA = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!qaQuery.trim() || !analysisResult || qaLoading) return;

    setQaLoading(true);
    try {
      const res = await api.imageQA(qaQuery, analysisResult.ocr_text, analysisResult.visual_type);
      setQaAnswer(res.answer);
    } catch (err: any) {
      alert(`QA failed: ${err.message}`);
    } finally {
      setQaLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            <ScanEye className="w-6 h-6 text-red-500" />
            Image & Screenshot Intelligence
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Analyze UI screenshots, lecture slides, diagrams, and scanned receipts locally using OpenCV and local OCR.
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleLoadSampleScreenshot}
            className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-xs border border-slate-700 transition-colors"
          >
            Load Sample Screenshot
          </button>
          <button
            onClick={() => fileInputRef.current?.click()}
            className="px-4 py-2 rounded-xl bg-red-600 hover:bg-red-500 text-white font-semibold text-xs transition-colors shadow-md shadow-red-950/40"
          >
            Upload Screenshot
          </button>
          <input
            ref={fileInputRef}
            type="file"
            className="hidden"
            accept=".png,.jpg,.jpeg,.webp"
            onChange={(e) => {
              if (e.target.files && e.target.files[0]) {
                handleImageFile(e.target.files[0]);
              }
            }}
          />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Image Preview or Upload Dropzone */}
        <div className="lg:col-span-6 space-y-4">
          <div
            onClick={() => fileInputRef.current?.click()}
            className={`rounded-3xl border-2 border-dashed p-4 min-h-[360px] flex flex-col items-center justify-center cursor-pointer transition-all ${
              imagePreviewUrl
                ? 'border-slate-800 bg-slate-900/60'
                : 'border-slate-800 hover:border-slate-700 bg-slate-900/30'
            }`}
          >
            {imagePreviewUrl ? (
              <div className="space-y-3 w-full">
                <img
                  src={imagePreviewUrl}
                  alt="Uploaded preview"
                  className="rounded-2xl max-h-[380px] w-full object-contain mx-auto bg-black/40 border border-slate-800"
                />
                <p className="text-center text-[11px] text-slate-500">
                  Click image to choose a different screenshot
                </p>
              </div>
            ) : (
              <div className="text-center space-y-3 max-w-xs">
                <div className="w-14 h-14 rounded-2xl bg-slate-800 flex items-center justify-center mx-auto text-slate-400">
                  <ImageIcon className="w-7 h-7" />
                </div>
                <p className="text-sm font-semibold text-slate-200">
                  Drop screenshot or click to upload
                </p>
                <p className="text-xs text-slate-500">
                  PNG, JPG, or WebP. Analyzed entirely on-device with zero cloud exposure.
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Visual Insights & OCR */}
        <div className="lg:col-span-6 space-y-4">
          {analyzing ? (
            <div className="h-full min-h-[360px] rounded-3xl bg-slate-900/40 border border-slate-800 flex flex-col items-center justify-center space-y-3">
              <div className="w-8 h-8 border-2 border-red-500 border-t-transparent rounded-full animate-spin"></div>
              <p className="text-xs text-slate-400">Running on-device computer vision & OCR pipeline...</p>
            </div>
          ) : analysisResult ? (
            <div className="space-y-4">
              {/* Classified Type & Meta */}
              <div className="p-5 rounded-3xl bg-slate-900/70 border border-slate-800 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full bg-red-500 animate-pulse"></span>
                    <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                      Visual Classification
                    </span>
                  </div>
                  <span className="text-[10px] text-emerald-400 font-semibold px-2 py-0.5 rounded-full bg-emerald-950/60 border border-emerald-500/30">
                    Processed in {analysisResult.latency_ms} ms
                  </span>
                </div>
                <div className="text-lg font-bold text-white flex items-center gap-2">
                  <Layout className="w-5 h-5 text-red-400" />
                  {analysisResult.visual_type}
                </div>
                <div className="grid grid-cols-3 gap-2 pt-2 border-t border-slate-800 text-xs">
                  <div>
                    <span className="text-slate-500 block text-[10px]">Dimensions</span>
                    <strong className="text-slate-300">
                      {analysisResult.dimensions.width} × {analysisResult.dimensions.height}
                    </strong>
                  </div>
                  <div>
                    <span className="text-slate-500 block text-[10px]">Text Regions</span>
                    <strong className="text-slate-300">{analysisResult.text_regions_count}</strong>
                  </div>
                  <div>
                    <span className="text-slate-500 block text-[10px]">Mean Luminance</span>
                    <strong className="text-slate-300">{analysisResult.mean_brightness}/255</strong>
                  </div>
                </div>
              </div>

              {/* Extracted Text & Layout Insights */}
              <div className="p-5 rounded-3xl bg-slate-900/70 border border-slate-800 space-y-3">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                  <Eye className="w-3.5 h-3.5 text-blue-400" />
                  Extracted Content & Key Findings
                </h4>
                <div className="p-3.5 rounded-2xl bg-slate-950/70 border border-slate-800/80 font-mono text-xs text-slate-300 max-h-40 overflow-y-auto whitespace-pre-wrap leading-relaxed">
                  {analysisResult.ocr_text}
                </div>
              </div>

              {/* Interactive Image Q&A */}
              <div className="p-5 rounded-3xl bg-slate-900/70 border border-slate-800 space-y-3">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                  <MessageSquare className="w-3.5 h-3.5 text-red-400" />
                  Ask Questions About This Image
                </h4>
                <form onSubmit={handleImageQA} className="flex gap-2">
                  <input
                    type="text"
                    value={qaQuery}
                    onChange={(e) => setQaQuery(e.target.value)}
                    placeholder="e.g., 'What deadlines or metrics are shown in this screenshot?'"
                    className="flex-1 bg-slate-950 text-xs text-slate-200 border border-slate-700 rounded-xl px-3 py-2 focus:outline-none focus:border-red-500"
                  />
                  <button
                    type="submit"
                    disabled={!qaQuery.trim() || qaLoading}
                    className="px-4 py-2 rounded-xl bg-red-600 hover:bg-red-500 disabled:opacity-40 text-white font-semibold text-xs flex items-center gap-1"
                  >
                    <span>Ask</span>
                    <Send className="w-3 h-3" />
                  </button>
                </form>

                {qaLoading && (
                  <p className="text-xs text-slate-400">Analyzing visual context locally...</p>
                )}
                {qaAnswer && (
                  <div className="p-3.5 rounded-2xl bg-red-950/20 border border-red-500/30 text-xs text-slate-200 space-y-1.5 leading-relaxed font-sans">
                    <span className="font-bold text-red-400 text-[11px] block">AI Answer:</span>
                    <div>{qaAnswer}</div>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="h-full min-h-[360px] rounded-3xl bg-slate-900/30 border border-slate-800 flex flex-col items-center justify-center p-8 text-center space-y-3">
              <ScanEye className="w-10 h-10 text-slate-600" />
              <h4 className="text-sm font-semibold text-slate-300">No Image Loaded</h4>
              <p className="text-xs text-slate-500 max-w-sm">
                Upload a screenshot or click "Load Sample Screenshot" above to test on-device OCR and visual breakdown.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
