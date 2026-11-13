import React, { useState } from 'react';
import { QueryClient, QueryClientProvider, useQuery } from '@tanstack/react-query';
import { Navbar } from './components/Navbar';
import { RiverMap } from './components/Map';
import { StationSidebar } from './components/StationSidebar';
import { fetchStations, fetchRegions } from './services/api';
import type { AlertLevel } from './types';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 30, // 30 seconds
      retry: 2,
    },
  },
});

const RiverMonitorDashboard: React.FC = () => {
  const [selectedRegion, setSelectedRegion] = useState<string | null>(null);
  const [selectedAlert, setSelectedAlert] = useState<AlertLevel | 'all'>('all');
  const [selectedStationId, setSelectedStationId] = useState<number | null>(null);

  // 1. Fetch Regions
  const { data: regions = [] } = useQuery({
    queryKey: ['regions'],
    queryFn: fetchRegions,
  });

  // 2. Fetch Stations GeoJSON (with optional region or alert filters)
  const { data: stationsData, isLoading } = useQuery({
    queryKey: ['stations', selectedRegion, selectedAlert],
    queryFn: () =>
      fetchStations({
        codice_istat: selectedRegion || undefined,
        stato_allerta: selectedAlert !== 'all' ? selectedAlert : undefined,
      }),
    refetchInterval: 45000, // Real-time polling every 45s
  });

  const stations = stationsData?.features || [];
  const totalStations = stationsData?.total_count || 0;

  // Selected station feature details (includes webcam_url)
  const selectedStationFeature = stations.find((s) => s.id === selectedStationId) || null;

  // Count stations currently exceeding thresholds
  const alertCount = stations.filter((s) => {
    const alert = s.properties.ultima_misurazione?.stato_allerta;
    return alert === 'giallo' || alert === 'arancione' || alert === 'rosso';
  }).length;

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-slate-950 font-sans">
      {/* Top Navigation & Global Filters */}
      <Navbar
        regions={regions}
        selectedRegion={selectedRegion}
        onSelectRegion={setSelectedRegion}
        selectedAlert={selectedAlert}
        onSelectAlert={setSelectedAlert}
        totalStations={totalStations}
        alertCount={alertCount}
      />

      {/* Main Content: Map & Right Sidebar */}
      <main className="flex-1 relative overflow-hidden">
        {isLoading && (
          <div className="absolute top-4 left-1/2 -translate-x-1/2 z-[2000] bg-slate-900/90 text-blue-400 px-4 py-2 rounded-full border border-slate-700 shadow-xl text-xs font-semibold flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-blue-400 animate-ping" />
            Caricamento dati idrometrici...
          </div>
        )}

        <RiverMap
          stations={stations}
          selectedStationId={selectedStationId}
          onSelectStation={(id) => setSelectedStationId(id)}
        />

        <StationSidebar
          stationId={selectedStationId}
          stationFeature={selectedStationFeature}
          onClose={() => setSelectedStationId(null)}
        />
      </main>
    </div>
  );
};

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <RiverMonitorDashboard />
    </QueryClientProvider>
  );
}
