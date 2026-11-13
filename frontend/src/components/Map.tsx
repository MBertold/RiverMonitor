import React from 'react';
import { MapContainer, TileLayer, CircleMarker, Tooltip } from 'react-leaflet';
import type { StazioneFeature, AlertLevel } from '../types';

interface MapProps {
  stations: StazioneFeature[];
  selectedStationId: number | null;
  onSelectStation: (id: number) => void;
}

const ALERT_COLORS: Record<AlertLevel, { fill: string; stroke: string; label: string }> = {
  verde: { fill: '#10b981', stroke: '#065f46', label: 'Regolare' },
  giallo: { fill: '#f59e0b', stroke: '#b45309', label: 'Attenzione' },
  arancione: { fill: '#f97316', stroke: '#9a3412', label: 'Preallarme' },
  rosso: { fill: '#ef4444', stroke: '#991b1b', label: 'Allarme' },
};

export const RiverMap: React.FC<MapProps> = ({
  stations,
  selectedStationId,
  onSelectStation,
}) => {
  return (
    <div className="w-full h-full relative">
      <MapContainer
        center={[42.8333, 12.8333]}
        zoom={6}
        scrollWheelZoom={true}
        className="w-full h-full"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          maxZoom={19}
        />

        {stations.map((st) => {
          const [lon, lat] = st.geometry.coordinates;
          const status = st.properties.ultima_misurazione?.stato_allerta || 'verde';
          const style = ALERT_COLORS[status];
          const isSelected = selectedStationId === st.id;

          return (
            <CircleMarker
              key={st.id}
              center={[lat, lon]}
              radius={isSelected ? 11 : (status === 'rosso' || status === 'arancione' ? 9 : 7)}
              pathOptions={{
                fillColor: style.fill,
                fillOpacity: isSelected ? 1 : 0.85,
                color: isSelected ? '#ffffff' : style.stroke,
                weight: isSelected ? 3 : 1.5,
              }}
              eventHandlers={{
                click: () => onSelectStation(st.id),
              }}
            >
              <Tooltip direction="top" offset={[0, -8]} opacity={0.95}>
                <div className="text-xs p-1 min-w-[160px]">
                  <p className="font-bold text-slate-900 text-sm">{st.properties.nome}</p>
                  <p className="text-slate-600 mb-1">
                    Fiume: <span className="font-medium text-slate-800">{st.properties.fiume || 'N/D'}</span>
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
      </MapContainer>

      {/* Floating Legend */}
      <div className="absolute bottom-6 left-6 z-[1000] bg-slate-900/90 backdrop-blur-md border border-slate-800 rounded-xl p-3 shadow-2xl text-xs text-slate-300">
        <p className="font-semibold text-slate-200 mb-2">Livelli di Allerta</p>
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
        </div>
      </div>
    </div>
  );
};
