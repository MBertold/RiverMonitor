import type { FeatureCollectionStazioni, StationTimeSeries, RegioneSummary, RiverFeatureCollection } from '../types';

const BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

export async function fetchStations(params?: {
  regione_id?: number;
  codice_istat?: string;
  fiume?: string;
  stato_allerta?: string;
  bbox?: string;
}): Promise<FeatureCollectionStazioni> {
  const query = new URLSearchParams();
  if (params?.regione_id) query.append('regione_id', params.regione_id.toString());
  if (params?.codice_istat) query.append('codice_istat', params.codice_istat);
  if (params?.fiume) query.append('fiume', params.fiume);
  if (params?.stato_allerta) query.append('stato_allerta', params.stato_allerta);
  if (params?.bbox) query.append('bbox', params.bbox);

  const url = `${BASE_URL}/stations${query.toString() ? `?${query.toString()}` : ''}`;
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Errore durante il recupero delle stazioni: ${response.statusText}`);
  }
  return response.json();
}

export async function fetchStationTimeSeries(stationId: number, hours: number = 48): Promise<StationTimeSeries> {
  const response = await fetch(`${BASE_URL}/stations/${stationId}/measurements?hours=${hours}`);
  if (!response.ok) {
    throw new Error(`Errore durante il recupero della serie storica: ${response.statusText}`);
  }
  return response.json();
}

export async function fetchRegions(): Promise<RegioneSummary[]> {
  const response = await fetch(`${BASE_URL}/regions`);
  if (!response.ok) {
    throw new Error(`Errore durante il recupero delle regioni: ${response.statusText}`);
  }
  return response.json();
}

export async function fetchRiversGeoJSON(): Promise<RiverFeatureCollection> {
  const response = await fetch(`${BASE_URL}/rivers/geojson`);
  if (!response.ok) {
    throw new Error(`Errore durante il recupero dei tracciati fluviali: ${response.statusText}`);
  }
  return response.json();
}
