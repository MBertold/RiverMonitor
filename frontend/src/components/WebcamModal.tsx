import React, { useState, useEffect } from 'react';
import { X, Video, ExternalLink, RefreshCw, MapPin, Waves, ShieldCheck } from 'lucide-react';
import type { WebcamFeature } from '../types';

interface WebcamModalProps {
  webcam: WebcamFeature | null;
  onClose: () => void;
}

export const WebcamModal: React.FC<WebcamModalProps> = ({ webcam, onClose }) => {
  const [timestamp, setTimestamp] = useState<number>(Date.now());
  const [autoRefresh, setAutoRefresh] = useState<boolean>(true);

  // Auto-refresh snapshot every 6 seconds for jpeg_stream
  useEffect(() => {
    if (!webcam || webcam.properties.tipo_feed !== 'jpeg_stream' || !autoRefresh) return;
    const interval = setInterval(() => {
      setTimestamp(Date.now());
    }, 6000);
    return () => clearInterval(interval);
  }, [webcam, autoRefresh]);

  if (!webcam) return null;

  const { nome, corso_dacqua, localita, regione, tipo_feed, url_feed, url_web, provider, descrizione } =
    webcam.properties;

  return (
    <div className="fixed inset-0 z-[3000] flex items-center justify-center bg-black/75 backdrop-blur-sm p-4 animate-fadeIn">
      <div className="relative w-full max-w-2xl bg-slate-900 border border-slate-700/80 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="px-5 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-900/90">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-purple-500/20 border border-purple-500/40 flex items-center justify-center text-purple-400">
              <Video className="w-5 h-5 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold uppercase tracking-wider text-purple-400">
                  Webcam Fluviale Live
                </span>
                <span className="text-[11px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                  {provider}
                </span>
              </div>
              <h3 className="text-base font-bold text-white leading-snug">{nome}</h3>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
            title="Chiudi"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Video / Snapshot Area */}
        <div className="flex-1 overflow-y-auto p-5 space-y-4">
          {tipo_feed === 'jpeg_stream' && url_feed ? (
            <div className="space-y-3">
              <div className="aspect-video w-full rounded-xl overflow-hidden bg-black border border-slate-700 relative shadow-inner group">
                <img
                  key={timestamp}
                  src={`${url_feed}?t=${timestamp}`}
                  alt={nome}
                  className="w-full h-full object-cover"
                />

                {/* Overlay Badge */}
                <div className="absolute top-3 left-3 bg-slate-950/80 backdrop-blur-md px-2.5 py-1 rounded-full border border-slate-700 text-[11px] font-semibold text-emerald-400 flex items-center gap-1.5 shadow">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
                  FEED IN DIRETTA
                </div>

                <div className="absolute bottom-3 right-3 bg-slate-950/80 backdrop-blur-md px-2.5 py-1 rounded-md text-[10px] text-slate-400 border border-slate-800">
                  Aggiornato: {new Date(timestamp).toLocaleTimeString()}
                </div>
              </div>

              {/* Controls bar */}
              <div className="flex items-center justify-between text-xs text-slate-400 px-1">
                <label className="flex items-center gap-2 cursor-pointer select-none">
                  <input
                    type="checkbox"
                    checked={autoRefresh}
                    onChange={(e) => setAutoRefresh(e.target.checked)}
                    className="rounded bg-slate-800 border-slate-700 text-purple-600 focus:ring-purple-500"
                  />
                  <span>Auto-aggiornamento continuo (6s)</span>
                </label>

                <button
                  onClick={() => setTimestamp(Date.now())}
                  className="flex items-center gap-1.5 text-purple-400 hover:text-purple-300 transition-colors font-medium"
                >
                  <RefreshCw className="w-3.5 h-3.5" />
                  Ricarica ora
                </button>
              </div>
            </div>
          ) : tipo_feed === 'iframe' && url_feed ? (
            <div className="aspect-video w-full rounded-xl overflow-hidden bg-black border border-slate-700 shadow-inner">
              <iframe
                src={url_feed}
                title={nome}
                className="w-full h-full border-0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
              />
            </div>
          ) : (
            /* External protected link (e.g. SkylineWebcams, Panomax, etc.) */
            <div className="p-6 bg-slate-800/40 border border-slate-700/60 rounded-xl space-y-4 text-center">
              <div className="w-16 h-16 rounded-2xl bg-purple-500/10 border border-purple-500/30 flex items-center justify-center text-purple-400 mx-auto">
                <ShieldCheck className="w-8 h-8" />
              </div>

              <div className="space-y-1.5">
                <h4 className="text-base font-bold text-white">Trasmissione Streaming HD Protetta</h4>
                <p className="text-xs text-slate-300 max-w-md mx-auto leading-relaxed">
                  Questa telecamera trasmette in alta definizione 24/7 sul circuito ufficiale{' '}
                  <span className="font-semibold text-purple-300">{provider}</span>. Le policy di sicurezza e copyright
                  richiedono la visualizzazione diretta sul portale del fornitore.
                </p>
              </div>

              <div className="pt-2">
                <a
                  href={url_web}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-semibold text-sm transition-all shadow-lg shadow-purple-600/30 hover:shadow-purple-500/50"
                >
                  <Video className="w-4 h-4" />
                  <span>Guarda la diretta streaming su {provider}</span>
                  <ExternalLink className="w-4 h-4" />
                </a>
              </div>
            </div>
          )}

          {/* Metadata Card */}
          <div className="bg-slate-800/50 border border-slate-700/80 rounded-xl p-4 space-y-3">
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs">
              <div>
                <span className="text-slate-400 block text-[11px]">Corso d'acqua</span>
                <span className="text-white font-semibold flex items-center gap-1 mt-0.5">
                  <Waves className="w-3.5 h-3.5 text-blue-400" />
                  {corso_dacqua}
                </span>
              </div>
              <div>
                <span className="text-slate-400 block text-[11px]">Località</span>
                <span className="text-white font-semibold flex items-center gap-1 mt-0.5">
                  <MapPin className="w-3.5 h-3.5 text-rose-400" />
                  {localita}
                </span>
              </div>
              <div>
                <span className="text-slate-400 block text-[11px]">Regione</span>
                <span className="text-white font-semibold mt-0.5 block">{regione}</span>
              </div>
            </div>

            {descrizione && (
              <p className="text-xs text-slate-400 leading-relaxed border-t border-slate-700/60 pt-3">
                {descrizione}
              </p>
            )}

            <div className="pt-2 border-t border-slate-700/60 flex items-center justify-between text-xs">
              <span className="text-slate-400 text-[11px]">Fornitore sorgente:</span>
              <a
                href={url_web}
                target="_blank"
                rel="noopener noreferrer"
                className="text-purple-400 hover:text-purple-300 font-medium inline-flex items-center gap-1"
              >
                <span>Sito ufficiale {provider}</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
