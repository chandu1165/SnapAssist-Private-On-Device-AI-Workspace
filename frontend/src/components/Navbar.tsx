import React from 'react';
import { ShieldCheck, Cpu, WifiOff, Lock, Sparkles } from 'lucide-react';

interface NavbarProps {
  activeTab: string;
  onNavigate: (tab: string) => void;
  isNpuActive?: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({ isNpuActive = false }) => {
  return (
    <header className="h-16 bg-slate-900/90 backdrop-blur-md border-b border-slate-800 px-6 flex items-center justify-between sticky top-0 z-50">
      {/* Brand & Identity */}
      <div className="flex items-center gap-3">
        <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-red-600 via-rose-600 to-amber-600 shadow-lg shadow-red-900/30">
          <Sparkles className="w-5 h-5 text-white" />
          <span className="absolute -bottom-1 -right-1 flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
          </span>
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
              SnapAssist
            </h1>
            <span className="text-[10px] uppercase tracking-wider font-bold px-1.5 py-0.5 rounded bg-red-950/80 border border-red-500/40 text-red-400">
              Snapdragon® AI
            </span>
          </div>
          <p className="text-xs text-slate-400 font-medium">
            Your files. Your AI. Your device.
          </p>
        </div>
      </div>

      {/* Trust & Telemetry Badges */}
      <div className="flex items-center gap-3">
        {/* Local Processing Pill */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-950/50 border border-emerald-500/30 text-emerald-400 text-xs font-semibold">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          <span>100% On-Device</span>
        </div>

        {/* NPU Target Pill */}
        <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-red-950/50 border border-red-500/30 text-red-300 text-xs font-semibold">
          <Cpu className="w-4 h-4 text-red-400" />
          <span>Hexagon™ NPU {isNpuActive ? '(Accelerated)' : '(45 TOPS Target)'}</span>
        </div>

        {/* Cloud Egress Pill */}
        <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800/60 border border-slate-700/60 text-slate-300 text-xs font-medium">
          <Lock className="w-3.5 h-3.5 text-slate-400" />
          <span>Cloud API: <strong className="text-white">0</strong></span>
        </div>

        {/* Offline Ready Pill */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-indigo-950/40 border border-indigo-500/30 text-indigo-300 text-xs font-medium">
          <WifiOff className="w-3.5 h-3.5 text-indigo-400" />
          <span className="hidden sm:inline">Offline Mode:</span>
          <span className="text-emerald-400 font-semibold">Ready</span>
        </div>
      </div>
    </header>
  );
};
