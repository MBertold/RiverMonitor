import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  X,
  TrendingUp,
  TrendingDown,
  Minus,
  Activity,
  Layers,
  MapPin,
  AlertCircle,
  Video,
  LineChart as ChartIcon,
  ExternalLink,
} from 'lucide-react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ReferenceLine,
} from 'recharts';
import { fetchStationTimeSeries } from '../services/api';
import type { StazioneFeature } from '../types';

interface StationSidebarProps {
  stationId: number | null;
  stationFeature?: StazioneFeature | null;
  onClose: () => void;
}

export const StationSidebar: React.FC<StationSidebarProps> = ({
  stationId,
  stationFeature,
  onClose,
}) => {
  const [hours, setHours] = useState<number>(48);
  const [activeTab, setActiveTab] = useState<'grafico' | 'webcam'>('grafico');

  const { data, isLoading, error } = useQuery({
    queryKey: ['station-timeseries', stationId, hours],
    queryFn: () => (stationId ? fetchStationTimeSeries(stationId, hours) : null),
    enabled: !!stationId,
    refetchInterval: 30000,
  });

  if (!stationId) return null;

  const webcamUrl = stationFeature?.properties.webcam_url;
  const fiumeNome = data?.fiume || stationFeature?.properties.fiume;

  // Format timestamp for chart XAxis
  const chartData = data?.serie_storica.map((item) => {
    const d = new Date(item.timestamp);
    const timeLabel = `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`;
    const dateLabel = `${d.getDate()}/${d.getMonth() + 1}`;
    return {
      rawTimestamp: item.timestamp,
      label: `${timeLabel} ${dateLabel}`,
      livello: item.livello,
      portata: item.portata,
      stato: item.stato_allerta,
    };
  }) || [];

  return (
    <aside className="absolute right-0 top-16 bottom-0 w-full sm:w-[480px] lg:w-[540px] bg-slate-900/95 backdrop-blur-xl border-l border-slate-800 shadow-2xl z-[1500] flex flex-col text-slate-200 transition-all">
      {/* Sidebar Header */}
      <div className="p-5 border-b border-slate-800 flex items-start justify-between bg-slate-950/40">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-mono uppercase bg-blue-500/10 text-blue-400 px-2 py-0.5 rounded border border-blue-500/20">
              {data?.codice_stazione || stationFeature?.properties.codice_stazione || 'STAZIONE'}
            </span>
            <span className="text-xs text-slate-400 flex items-center gap-1">
              <MapPin className="w-3.5 h-3.5 text-slate-500" />
              {data?.regione || stationFeature?.properties.regione_nome || ''}
            </span>
          </div>

          <h2 className="text-lg font-bold text-white tracking-tight">
            {data?.nome || stationFeature?.properties.nome || 'Dettaglio Stazione'}
          </h2>

          <p className="text-sm text-slate-400 mt-1">
            Corso d'acqua: <span className="text-slate-100 font-semibold">{fiumeNome || 'N/D'}</span>
          </p>
        </div>

        <button
          onClick={onClose}
          className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          title="Chiudi pannello"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Tabs Switcher: Idrogramma vs Webcam Live */}
      <div className="flex border-b border-slate-800 px-5 pt-2 bg-slate-950/20">
        <button
          onClick={() => setActiveTab('grafico')}
          className={`flex items-center gap-2 px-4 py-2.5 text-xs font-semibold border-b-2 transition-all ${
            activeTab === 'grafico'
              ? 'border-blue-500 text-blue-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <ChartIcon className="w-3.5 h-3.5" />
          Idrogramma & Serie Storica
        </button>
        <button
          onClick={() => setActiveTab('webcam')}
          className={`flex items-center gap-2 px-4 py-2.5 text-xs font-semibold border-b-2 transition-all relative ${
            activeTab === 'webcam'
              ? 'border-red-500 text-red-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Video className="w-3.5 h-3.5" />
          Webcam Live
          {webcamUrl && (
            <span className="w-2 h-2 rounded-full bg-red-500 animate-ping absolute -top-0.5 right-2" />
          )}
        </button>
      </div>

      {isLoading && activeTab === 'grafico' && (
        <div className="flex-1 flex flex-col items-center justify-center p-8 text-slate-400">
          <Activity className="w-8 h-8 animate-spin text-blue-500 mb-3" />
          <p className="text-sm">Caricamento serie idrometrica in tempo reale...</p>
        </div>
      )}

      {error && activeTab === 'grafico' && (
        <div className="flex-1 flex flex-col items-center justify-center p-8 text-red-400 text-center">
          <AlertCircle className="w-8 h-8 mb-2" />
          <p className="text-sm">Impossibile recuperare i dati della stazione.</p>
        </div>
      )}

      {/* TAB 1: IDROGRAMMA & METRICHE */}
      {activeTab === 'grafico' && data && !isLoading && (
        <div className="flex-1 overflow-y-auto p-5 space-y-6">
          {/* Key Metric Cards */}
          <div className="grid grid-cols-3 gap-3">
            <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-3">
              <span className="text-xs text-slate-400 block mb-1">Livello Attuale</span>
              <div className="flex items-baseline gap-1">
                <span className="text-xl font-bold text-white">
                  {data.stats.current_livello !== null ? `${data.stats.current_livello}` : '--'}
                </span>
                <span className="text-xs text-slate-400">m</span>
              </div>
            </div>

            <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-3">
              <span className="text-xs text-slate-400 block mb-1">Variazione 24h</span>
              <div className="flex items-center gap-1">
                {data.stats.trend === 'in_aumento' && <TrendingUp className="w-4 h-4 text-red-400" />}
                {data.stats.trend === 'in_calo' && <TrendingDown className="w-4 h-4 text-emerald-400" />}
                {data.stats.trend === 'stazionario' && <Minus className="w-4 h-4 text-slate-400" />}
                <span
                  className={`text-sm font-semibold ${
                    (data.stats.delta_livello_24h || 0) > 0 ? 'text-amber-400' : 'text-emerald-400'
                  }`}
                >
                  {data.stats.delta_livello_24h !== null
                    ? `${data.stats.delta_livello_24h > 0 ? '+' : ''}${data.stats.delta_livello_24h} m`
                    : '--'}
                </span>
              </div>
            </div>

            <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-3">
              <span className="text-xs text-slate-400 block mb-1">Picco Massimo</span>
              <div className="flex items-baseline gap-1">
                <span className="text-xl font-bold text-white">
                  {data.stats.max_livello !== null ? `${data.stats.max_livello}` : '--'}
                </span>
                <span className="text-xs text-slate-400">m</span>
              </div>
            </div>
          </div>

          {/* Chart Header & Timeframe Switcher */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Activity className="w-4 h-4 text-blue-400" />
                <h3 className="text-sm font-semibold text-slate-200">Andamento Idrometrico (Idrogramma)</h3>
              </div>
              <div className="flex items-center bg-slate-800 rounded-lg p-0.5 text-xs">
                <button
                  onClick={() => setHours(24)}
                  className={`px-2.5 py-1 rounded-md transition-colors ${
                    hours === 24 ? 'bg-blue-600 text-white font-medium' : 'text-slate-400 hover:text-white'
                  }`}
                >
                  24h
                </button>
                <button
                  onClick={() => setHours(48)}
                  className={`px-2.5 py-1 rounded-md transition-colors ${
                    hours === 48 ? 'bg-blue-600 text-white font-medium' : 'text-slate-400 hover:text-white'
                  }`}
                >
                  48h
                </button>
              </div>
            </div>

            {/* Recharts Hydrograph */}
            <div className="h-64 w-full bg-slate-950/60 border border-slate-800 rounded-xl p-3 pt-4">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} />
                  <XAxis
                    dataKey="label"
                    stroke="#94a3b8"
                    fontSize={11}
                    tickLine={false}
                    interval="preserveStartEnd"
                  />
                  <YAxis
                    stroke="#94a3b8"
                    fontSize={11}
                    tickLine={false}
                    domain={['auto', 'auto']}
                    unit="m"
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#0f172a',
                      borderColor: '#334155',
                      borderRadius: '0.75rem',
                      fontSize: '12px',
                    }}
                    labelStyle={{ color: '#cbd5e1', fontWeight: 600 }}
                  />

                  {data.soglie.gialla && (
                    <ReferenceLine
                      y={data.soglie.gialla}
                      stroke="#f59e0b"
                      strokeDasharray="4 4"
                      label={{ value: 'Gialla', fill: '#f59e0b', fontSize: 10, position: 'right' }}
                    />
                  )}
                  {data.soglie.arancione && (
                    <ReferenceLine
                      y={data.soglie.arancione}
                      stroke="#f97316"
                      strokeDasharray="4 4"
                      label={{ value: 'Arancione', fill: '#f97316', fontSize: 10, position: 'right' }}
                    />
                  )}
                  {data.soglie.rossa && (
                    <ReferenceLine
                      y={data.soglie.rossa}
                      stroke="#ef4444"
                      strokeDasharray="4 4"
                      label={{ value: 'Rossa', fill: '#ef4444', fontSize: 10, position: 'right' }}
                    />
                  )}

                  <Line
                    type="monotone"
                    dataKey="livello"
                    name="Livello Idrometrico"
                    stroke="#38bdf8"
                    strokeWidth={2.5}
                    dot={false}
                    activeDot={{ r: 5, fill: '#38bdf8', stroke: '#ffffff' }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Official Thresholds Table */}
          <div className="bg-slate-800/40 border border-slate-800 rounded-xl p-4 space-y-2">
            <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2 flex items-center gap-1.5">
              <Layers className="w-3.5 h-3.5 text-slate-400" />
              Soglie Idrometriche Ufficiali
            </h4>
            <div className="grid grid-cols-3 gap-2 text-center text-xs">
              <div className="p-2 rounded-lg bg-amber-500/10 border border-amber-500/20">
                <span className="text-amber-400 font-medium block">Allerta Gialla</span>
                <span className="text-sm font-bold text-white">
                  {data.soglie.gialla !== null ? `${data.soglie.gialla} m` : 'N/D'}
                </span>
              </div>
              <div className="p-2 rounded-lg bg-orange-500/10 border border-orange-500/20">
                <span className="text-orange-400 font-medium block">Allerta Arancione</span>
                <span className="text-sm font-bold text-white">
                  {data.soglie.arancione !== null ? `${data.soglie.arancione} m` : 'N/D'}
                </span>
              </div>
              <div className="p-2 rounded-lg bg-red-500/10 border border-red-500/20">
                <span className="text-red-400 font-medium block">Allerta Rossa</span>
                <span className="text-sm font-bold text-white">
                  {data.soglie.rossa !== null ? `${data.soglie.rossa} m` : 'N/D'}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: WEBCAM LIVE STREAMING */}
      {activeTab === 'webcam' && (
        <div className="flex-1 overflow-y-auto p-5 space-y-5">
          {webcamUrl ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-red-500 animate-ping" />
                  <span className="text-xs font-bold uppercase tracking-wider text-red-400">
                    Trasmissione Live Fluviale
                  </span>
                </div>
                <span className="text-xs text-slate-400">{data?.nome || 'Stazione'}</span>
              </div>

              {/* Player Container */}
              <div className="aspect-video w-full rounded-2xl overflow-hidden bg-black border border-slate-700/80 shadow-2xl relative">
                {webcamUrl.endsWith('.jpg') || webcamUrl.endsWith('.jpeg') ? (
                  <img
                    src={`${webcamUrl}?t=${Date.now()}`}
                    alt="Webcam Idrometrica Live"
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <iframe
                    src={webcamUrl}
                    title="Live River Webcam"
                    className="w-full h-full border-0"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                    allowFullScreen
                  />
                )}
              </div>

              <div className="bg-slate-800/40 border border-slate-800 rounded-xl p-4 text-xs text-slate-300 space-y-2">
                <p className="font-semibold text-white flex items-center gap-1.5">
                  <Video className="w-4 h-4 text-sky-400" />
                  Dettagli Flusso Video
                </p>
                <p className="text-slate-400 leading-relaxed">
                  Webcam ottica ad alta risoluzione puntata sulla sezione fluviale di misura per la verifica visiva
                  immediata dell'onda di piena, detriti flottanti e deflusso sotto le campate dei ponti.
                </p>
                <a
                  href={webcamUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 text-blue-400 hover:text-blue-300 font-medium pt-1"
                >
                  <span>Apri flusso sorgente a schermo intero</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center text-center p-8 bg-slate-950/40 border border-dashed border-slate-800 rounded-2xl">
              <div className="w-14 h-14 rounded-2xl bg-purple-500/10 border border-purple-500/30 flex items-center justify-center text-purple-400 mb-4">
                <Video className="w-7 h-7" />
              </div>
              <h3 className="text-base font-bold text-white mb-1">Nessuna Telecamera in questo Idrometro</h3>
              <p className="text-xs text-slate-400 max-w-sm mb-4 leading-relaxed">
                Questo sensore trasmette telemetria idrometrica di livello e portata. Le telecamere e le dirette streaming
                sui corsi d'acqua sono disponibili nel layer dedicato <span className="text-purple-300 font-semibold">Webcam Fiumi 📷</span> sulla mappa.
              </p>
            </div>
          )}
        </div>
      )}
    </aside>
  );
};
