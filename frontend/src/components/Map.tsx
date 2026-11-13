import React from 'react';
import { MapContainer, TileLayer, CircleMarker, Marker, Tooltip } from 'react-leaflet';
import L from 'leaflet';
import type { LatLngBoundsExpression } from 'leaflet';
import type { StazioneFeature, AlertLevel, WebcamFeature } from '../types';

interface MapProps {
  stations: StazioneFeature[];
  selectedStationId: number | null;
  onSelectStation: (id: number) => void;
  webcams: WebcamFeature[];
  showWebcams: boolean;
  onSelectWebcam: (webcam: WebcamFeature) => void;
}

// Bounding box rigoroso circoscritto alla Repubblica Italiana
const ITALY_BOUNDS: LatLngBoundsExpression = [
  [35.0, 6.0],  // Sud-Ovest (Isole Pelagie, Pantelleria, Sicilia)
  [47.5, 19.0], // Nord-Est (Alpi Retiche, Friuli, Puglia)
];

const ALERT_COLORS: Record<AlertLevel, { fill: string; stroke: string; label: string }> = {
  verde: { fill: '#10b981', stroke: '#065f46', label: 'Regolare' },
  giallo: { fill: '#f59e0b', stroke: '#b45309', label: 'Attenzione' },
  arancione: { fill: '#f97316', stroke: '#9a3412', label: 'Preallarme' },
  rosso: { fill: '#ef4444', stroke: '#991b1b', label: 'Allarme' },
};

// Custom DivIcon for independent river webcams
const webcamIcon = L.divIcon({
  className: 'custom-webcam-marker',
  html: `<div style="
    width: 28px;
    height: 28px;
    background: linear-gradient(135deg, #a855f7, #7e22ce);
    border: 2px solid #ffffff;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 12px rgba(168, 85, 247, 0.6);
    color: white;
    font-size: 13px;
    cursor: pointer;
    transition: transform 0.2s ease;
  ">📷</div>`,
  iconSize: [28, 28],
  iconAnchor: [14, 14],
});

export const RiverMap: React.FC<MapProps> = ({
  stations,
  selectedStationId,
  onSelectStation,
  webcams,
  showWebcams,
  onSelectWebcam,
}) => {
  return (
    <div className="w-full h-full relative">
      <MapContainer
        center={[42.50, 12.50]}
        zoom={6}
        minZoom={5.5}
        maxZoom={18}
        maxBounds={ITALY_BOUNDS}
        maxBoundsViscosity={1.0} // Impedisce completamente il trascinamento fuori dall'Italia
        scrollWheelZoom={true}
        className="w-full h-full"
      >
        {/* Layer Cartografico OpenStreetMap (100% Free & Open) */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          maxZoom={19}
        />

        {/* Stazioni Idrometriche Georeferenziate (CircleMarker) */}
        {stations.map((st) => {
          const [lon, lat] = st.geometry.coordinates;
          const status = st.properties.ultima_misurazione?.stato_allerta || 'verde';
          const style = ALERT_COLORS[status];
          const isSelected = selectedStationId === st.id;

          return (
            <CircleMarker
              key={`station-${st.id}`}
              center={[lat, lon]}
              radius={isSelected ? 12 : (status === 'rosso' || status === 'arancione' ? 9 : 7)}
              pathOptions={{
                fillColor: style.fill,
                fillOpacity: isSelected ? 1 : 0.85,
                color: isSelected ? '#ffffff' : style.stroke,
                weight: isSelected ? 3.5 : 1.5,
              }}
              eventHandlers={{
                click: (e) => {
                  e.originalEvent.stopPropagation();
                  onSelectStation(st.id);
                },
              }}
            >
              <Tooltip direction="top" offset={[0, -8]} opacity={0.95}>
                <div className="text-xs p-1 min-w-[170px]">
                  <p className="font-bold text-slate-900 text-sm">{st.properties.nome}</p>
                  <p className="text-slate-600 mb-1">
                    Fiume: <span className="font-semibold text-slate-800">{st.properties.fiume || 'N/D'}</span>
                  </p>
                  <div className="flex items-center justify-between border-t border-slate-200 pt-1 mt-1">
                    <span className="text-slate-600">Livello attuale:</span>
                    <span className="font-semibold text-slate-900">
                      {st.properties.ultima_misurazione?.livello_idrometrico !== null
                        ? `${st.properties.ultima_misurazione?.livello_idrometrico} m`
                        : 'N/D'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between mt-0.5">
                    <span className="text-slate-600">Stato:</span>
                    <span
                      className="text-[10px] uppercase font-bold px-1.5 py-0.5 rounded"
                      style={{ backgroundColor: `${style.fill}20`, color: style.fill }}
                    >
                      {style.label}
                    </span>
                  </div>
                </div>
              </Tooltip>
            </CircleMarker>
          );
        })}

        {/* Layer Webcam Fluviali Indipendenti (Marker con icona telecamera) */}
        {showWebcams &&
          webcams.map((wb) => {
            const [lon, lat] = wb.geometry.coordinates;
            return (
              <Marker
                key={`webcam-${wb.id}`}
                position={[lat, lon]}
                icon={webcamIcon}
                eventHandlers={{
                  click: (e) => {
                    e.originalEvent.stopPropagation();
                    onSelectWebcam(wb);
                  },
                }}
              >
                <Tooltip direction="top" offset={[0, -14]} opacity={0.95}>
                  <div className="text-xs p-1 min-w-[180px]">
                    <div className="flex items-center gap-1.5 text-purple-700 font-bold text-[11px] uppercase mb-0.5">
                      <span>📹 Webcam Fluviale</span>
                      {wb.properties.tipo_feed === 'jpeg_stream' && (
                        <span className="text-[9px] bg-emerald-100 text-emerald-800 px-1 py-0.2 rounded font-semibold">
                          Live Feed
                        </span>
                      )}
                    </div>
                    <p className="font-bold text-slate-900 text-sm leading-snug">{wb.properties.nome}</p>
                    <p className="text-slate-600 mt-1">
                      Corso d'acqua:{' '}
                      <span className="font-semibold text-slate-800">{wb.properties.corso_dacqua}</span>
                    </p>
                    <p className="text-slate-600">
                      Località: <span className="font-semibold text-slate-800">{wb.properties.localita}</span>
                    </p>
                    <p className="text-[10px] text-purple-600 mt-1.5 font-bold">Clicca per aprire la diretta</p>
                  </div>
                </Tooltip>
              </Marker>
            );
          })}
      </MapContainer>

      {/* Floating Info & Legend */}
      <div className="absolute bottom-6 left-6 z-[1000] bg-slate-900/90 backdrop-blur-md border border-slate-800 rounded-xl p-3 shadow-2xl text-xs text-slate-300">
        <div className="flex items-center justify-between gap-4 mb-2 pb-1.5 border-b border-slate-800">
          <p className="font-semibold text-slate-200">Legenda Mappa</p>
          <span className="text-[10px] text-slate-400">Solo Italia</span>
        </div>
        <div className="space-y-1.5">
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-emerald-500 shadow-sm" />
            <span>Regolare (Verde)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-amber-500 shadow-sm" />
            <span>Attenzione (Giallo)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-orange-500 shadow-sm" />
            <span>Preallarme (Arancione)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-red-500 shadow-sm animate-pulse" />
            <span>Allarme (Rosso)</span>
          </div>
          {showWebcams && (
            <div className="flex items-center gap-2 pt-1 border-t border-slate-800 text-purple-300">
              <span className="w-3.5 h-3.5 rounded-full bg-purple-500 flex items-center justify-center text-[8px] text-white">
                📷
              </span>
              <span>Webcam Fluviali ({webcams.length})</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
