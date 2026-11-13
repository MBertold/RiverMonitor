import React from 'react';
import { Waves, AlertTriangle, CheckCircle2, ShieldAlert, Video } from 'lucide-react';
import type { RegioneSummary, AlertLevel } from '../types';

interface NavbarProps {
  regions: RegioneSummary[];
  selectedRegion: string | null;
  onSelectRegion: (istat: string | null) => void;
  selectedAlert: AlertLevel | 'all';
  onSelectAlert: (alert: AlertLevel | 'all') => void;
  showWebcams: boolean;
  onToggleWebcams: () => void;
  webcamCount: number;
  totalStations: number;
  alertCount: number;
}

export const Navbar: React.FC<NavbarProps> = ({
  regions,
  selectedRegion,
  onSelectRegion,
  selectedAlert,
  onSelectAlert,
  showWebcams,
  onToggleWebcams,
  webcamCount,
  totalStations,
  alertCount,
}) => {
  return (
    <header className="h-16 bg-slate-900 border-b border-slate-800 px-4 flex items-center justify-between z-30 relative select-none">
      {/* Brand & Live status */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-blue-600/20 border border-blue-500/40 flex items-center justify-center text-blue-400 shadow-inner">
          <Waves className="w-6 h-6 animate-pulse" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="font-bold text-lg text-white tracking-tight">RiverMonitor</span>
            <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
              Live Italia
            </span>
          </div>
          <p className="text-xs text-slate-400 hidden sm:block">Monitoraggio Idrometrico Fiumi Italiani</p>
        </div>
      </div>

      {/* Center/Right Filters: Region, Webcams & Alert Level */}
      <div className="flex items-center gap-2 sm:gap-3">
        {/* Toggle Webcam Layer Button */}
        <button
          onClick={onToggleWebcams}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all ${
            showWebcams
              ? 'bg-purple-600/30 text-purple-200 border-purple-500/50 shadow-lg shadow-purple-600/20'
              : 'bg-slate-800 text-slate-400 border-slate-700 hover:text-slate-200'
          }`}
          title="Mostra/Nascondi layer webcam fluviali e ponti"
        >
          <Video className="w-3.5 h-3.5 text-purple-400" />
          <span className="hidden sm:inline">Webcam Fiumi</span>
          <span className="text-[11px] px-1.5 py-0.2 rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/30">
            {webcamCount}
          </span>
          <span className={`w-1.5 h-1.5 rounded-full ${showWebcams ? 'bg-purple-400 animate-ping' : 'bg-slate-500'}`} />
        </button>

        {/* Region Selector */}
        <select
          value={selectedRegion || ''}
          onChange={(e) => onSelectRegion(e.target.value ? e.target.value : null)}
          className="bg-slate-800 text-slate-200 text-sm rounded-lg px-3 py-1.5 border border-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">Tutte le 20 Regioni</option>
          {regions.map((reg) => (
            <option key={reg.codice_istat} value={reg.codice_istat}>
              {reg.nome} ({reg.totale_stazioni})
            </option>
          ))}
        </select>

        {/* Alert status pills */}
        <div className="hidden lg:flex items-center bg-slate-800/80 p-1 rounded-lg border border-slate-700/80 text-xs font-medium">
          <button
            onClick={() => onSelectAlert('all')}
            className={`px-2.5 py-1 rounded-md transition-colors ${
              selectedAlert === 'all' ? 'bg-slate-700 text-white shadow' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Tutte ({totalStations})
          </button>
          <button
            onClick={() => onSelectAlert('verde')}
            className={`px-2.5 py-1 rounded-md transition-colors flex items-center gap-1 ${
              selectedAlert === 'verde' ? 'bg-emerald-600/30 text-emerald-300 border border-emerald-500/40 shadow' : 'text-slate-400 hover:text-emerald-400'
            }`}
          >
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            Regolare
          </button>
          <button
            onClick={() => onSelectAlert('giallo')}
            className={`px-2.5 py-1 rounded-md transition-colors flex items-center gap-1 ${
              selectedAlert === 'giallo' ? 'bg-amber-600/30 text-amber-300 border border-amber-500/40 shadow' : 'text-slate-400 hover:text-amber-400'
            }`}
          >
            <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
            Giallo
          </button>
          <button
            onClick={() => onSelectAlert('arancione')}
            className={`px-2.5 py-1 rounded-md transition-colors flex items-center gap-1 ${
              selectedAlert === 'arancione' ? 'bg-orange-600/30 text-orange-300 border border-orange-500/40 shadow' : 'text-slate-400 hover:text-orange-400'
            }`}
          >
            <AlertTriangle className="w-3.5 h-3.5 text-orange-400" />
            Arancione
          </button>
          <button
            onClick={() => onSelectAlert('rosso')}
            className={`px-2.5 py-1 rounded-md transition-colors flex items-center gap-1 ${
              selectedAlert === 'rosso' ? 'bg-red-600/30 text-red-300 border border-red-500/40 shadow' : 'text-slate-400 hover:text-red-400'
            }`}
          >
            <ShieldAlert className="w-3.5 h-3.5 text-red-400" />
            Rosso
          </button>
        </div>

        {/* Global Alert Badge */}
        {alertCount > 0 ? (
          <div className="flex items-center gap-1.5 px-3 py-1 bg-red-500/10 border border-red-500/30 text-red-400 rounded-lg text-xs font-semibold animate-pulse">
            <ShieldAlert className="w-4 h-4" />
            <span>{alertCount} allerte</span>
          </div>
        ) : (
          <div className="flex items-center gap-1.5 px-3 py-1 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 rounded-lg text-xs font-medium">
            <CheckCircle2 className="w-4 h-4" />
            <span>Regolare</span>
          </div>
        )}
      </div>
    </header>
  );
};
