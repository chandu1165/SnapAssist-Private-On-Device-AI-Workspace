import React from 'react';
import {
  LayoutDashboard,
  FileText,
  MessageSquareCode,
  Search,
  ScanEye,
  Cpu,
  ShieldCheck,
  Settings,
  ChevronRight,
  Zap,
} from 'lucide-react';

interface SidebarProps {
  activeTab: string;
  onNavigate: (tab: string) => void;
  documentCount?: number;
  totalQueries?: number;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  onNavigate,
  documentCount = 0,
  totalQueries = 0,
}) => {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'documents', label: 'Documents', icon: FileText, badge: documentCount },
    { id: 'workspace', label: 'AI Workspace', icon: MessageSquareCode, badge: totalQueries > 0 ? `${totalQueries} queries` : undefined },
    { id: 'search', label: 'Semantic Search', icon: Search },
    { id: 'images', label: 'Image Analysis', icon: ScanEye },
    { id: 'performance', label: 'Performance', icon: Cpu },
    { id: 'privacy', label: 'Privacy Dashboard', icon: ShieldCheck, highlight: true },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <aside className="w-64 bg-slate-900/60 border-r border-slate-800 flex flex-col justify-between p-4 select-none shrink-0">
      <div className="space-y-1">
        <div className="px-3 py-2 text-[11px] font-bold uppercase tracking-wider text-slate-400">
          Navigation
        </div>
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
                isActive
                  ? 'bg-gradient-to-r from-red-600/20 to-red-500/10 text-white border border-red-500/30 shadow-sm shadow-red-950/50'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              <div className="flex items-center gap-3">
                <Icon
                  className={`w-4 h-4 transition-colors ${
                    isActive ? 'text-red-500' : item.highlight ? 'text-emerald-400' : 'text-slate-400'
                  }`}
                />
                <span className={item.highlight && !isActive ? 'text-slate-200 font-semibold' : ''}>
                  {item.label}
                </span>
              </div>
              <div className="flex items-center gap-1.5">
                {item.badge !== undefined && (
                  <span
                    className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                      isActive
                        ? 'bg-red-500 text-white'
                        : 'bg-slate-800 text-slate-300 border border-slate-700'
                    }`}
                  >
                    {item.badge}
                  </span>
                )}
                {isActive && <ChevronRight className="w-3.5 h-3.5 text-red-500" />}
              </div>
            </button>
          );
        })}
      </div>

      {/* Snapdragon Status Card */}
      <div className="mt-6 rounded-2xl bg-gradient-to-b from-slate-800/60 to-slate-950/80 border border-slate-700/50 p-3.5 text-xs">
        <div className="flex items-center gap-2 mb-2">
          <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></div>
          <span className="font-bold text-slate-200 uppercase tracking-wider text-[10px]">
            Qualcomm® AI Runtime
          </span>
        </div>
        <p className="text-slate-400 leading-relaxed mb-2 text-[11px]">
          Targeting <strong className="text-white">Snapdragon X Elite</strong> Hexagon NPU via ONNX QNN Provider.
        </p>
        <div className="flex items-center justify-between pt-2 border-t border-slate-800 text-[10px] text-slate-400">
          <span>Inference: Local</span>
          <span className="text-emerald-400 font-bold flex items-center gap-1">
            <Zap className="w-3 h-3 text-emerald-400" /> 0 Cloud API
          </span>
        </div>
      </div>
    </aside>
  );
};
