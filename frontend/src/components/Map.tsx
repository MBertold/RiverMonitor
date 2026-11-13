import React, { useEffect } from 'react';
import { MapContainer, TileLayer, CircleMarker, Polyline, Tooltip, useMap } from 'react-leaflet';
import type { LatLngBoundsExpression } from 'leaflet';
import type { StazioneFeature, AlertLevel, RiverFeature } from '../types';

interface MapProps {
  stations: StazioneFeature[];
  rivers: RiverFeature[];
  selectedStationId: number | null;
  onSelectStation: (id: number) => void;
  selectedRiver: string | null;
  onSelectRiver: (riverName: string | null) => void;
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

// Componente helper per gestire zoom e centratura dinamica
const MapController: React.FC<{
  selectedRiver: string | null;
  rivers: RiverFeature[];
}> = ({ selectedRiver, rivers }) => {
  const map = useMap();

  useEffect(() => {
    if (!selectedRiver) return;
    const river = rivers.find((r) => r.properties.nome.toLowerCase() === selectedRiver.toLowerCase());
    if (river && river.geometry.coordinates.length > 0) {
      const latLngs = river.geometry.coordinates.map(([lon, lat]) => [lat, lon] as [number, number]);
      map.fitBounds(latLngs, { padding: [60, 60], maxZoom: 10, animate: true });
    }
  }, [selectedRiver, rivers, map]);

  return null;
};

export const RiverMap: React.FC<MapProps> = ({
  stations,
  rivers,
  selectedStationId,
  onSelectStation,
  selectedRiver,
  onSelectRiver,
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
        <MapController selectedRiver={selectedRiver} rivers={rivers} />

        {/* Layer Cartografico OpenStreetMap (100% Free & Open) */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          maxZoom={19}
        />

        {/* Tracciati Vettoriali dei Fiumi (LineString) */}
        {rivers.map((river) => {
          const latLngs = river.geometry.coordinates.map(([lon, lat]) => [lat, lon] as [number, number]);
          const isSelected = selectedRiver?.toLowerCase() === river.properties.nome.toLowerCase();

          return (
            <Polyline
              key={`river-${river.id}`}
              positions={latLngs}
              pathOptions={{
                color: isSelected ? '#0284c7' : '#0284c7',
                weight: isSelected ? 6.5 : 3.0,
                opacity: isSelected ? 1.0 : 0.65,
                lineCap: 'round',
                lineJoin: 'round',
                dashArray: isSelected ? undefined : undefined,
              }}
              eventHandlers={{
                click: (e) => {
                  e.originalEvent.stopPropagation();
                  onSelectRiver(isSelected ? null : river.properties.nome);
                },
              }}
            >
              <Tooltip direction="top" offset={[0, -5]} opacity={0.95}>
                <div className="text-xs p-1">
                  <div className="flex items-center gap-1.5 font-bold text-sky-900 text-sm">
                    <span>Fiume {river.properties.nome}</span>
                    {river.properties.lunghezza_km && (
                      <span className="text-[10px] font-normal text-slate-500">
                        (~{river.properties.lunghezza_km} km)
                      </span>
                    )}
                  </div>
                  <p className="text-[11px] text-slate-600 mt-0.5">
                    Regioni: <span className="text-slate-800">{river.properties.regioni_attraversate || 'N/D'}</span>
                  </p>
                  <p className="text-[10px] text-sky-600 font-medium mt-1">
                    {isSelected ? '✓ Tracciato evidenziato (clicca per deselezionare)' : '👉 Clicca per evidenziare il tracciato'}
                  </p>
                </div>
              </Tooltip>
            </Polyline>
          );
        })}

        {/* Stazioni Idrometriche Georeferenziate (CircleMarker) */}
        {stations.map((st) => {
          const [lon, lat] = st.geometry.coordinates;
          const status = st.properties.ultima_misurazione?.stato_allerta || 'verde';
          const style = ALERT_COLORS[status];
          const isSelected = selectedStationId === st.id;
          const isStationOnSelectedRiver =
            selectedRiver && st.properties.fiume?.toLowerCase() === selectedRiver.toLowerCase();

          return (
            <CircleMarker
              key={`station-${st.id}`}
              center={[lat, lon]}
              radius={
                isSelected ? 12 : (isStationOnSelectedRiver ? 10 : (status === 'rosso' || status === 'arancione' ? 9 : 7))
              }
              pathOptions={{
                fillColor: style.fill,
                fillOpacity: isSelected || isStationOnSelectedRiver ? 1 : 0.85,
                color: isSelected ? '#ffffff' : (isStationOnSelectedRiver ? '#0284c7' : style.stroke),
                weight: isSelected ? 3.5 : (isStationOnSelectedRiver ? 2.5 : 1.5),
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
                    Fiume: <span className="font-semibold text-sky-700">{st.properties.fiume || 'N/D'}</span>
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
                  {st.properties.webcam_url && (
                    <div className="mt-1 pt-1 border-t border-slate-100 flex items-center gap-1 text-[10px] text-red-600 font-semibold">
                      <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-ping" />
                      Webcam Live attiva
                    </div>
                  )}
                </div>
              </Tooltip>
            </CircleMarker>
          );
        })}
      </MapContainer>

      {/* Floating Info & Legend */}
      <div className="absolute bottom-6 left-6 z-[1000] bg-slate-900/90 backdrop-blur-md border border-slate-800 rounded-xl p-3 shadow-2xl text-xs text-slate-300">
        <div className="flex items-center justify-between gap-4 mb-2 pb-1.5 border-b border-slate-800">
          <p className="font-semibold text-slate-200">Legenda Idrometrica</p>
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
          <div className="flex items-center gap-2 pt-1 border-t border-slate-800/80">
            <span className="w-5 h-1 rounded bg-sky-500" />
            <span>Tracciato Fiume (cliccabile)</span>
          </div>
        </div>
      </div>
    </div>
  );
};
