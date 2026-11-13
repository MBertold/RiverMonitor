export type AlertLevel = 'verde' | 'giallo' | 'arancione' | 'rosso';

export interface UltimaMisurazione {
  timestamp: string;
  livello_idrometrico: number | null;
  portata: number | null;
  stato_allerta: AlertLevel;
}

export interface StazioneProperties {
  id: number;
  codice_stazione: string;
  nome: string;
  fiume: string | null;
  quota_zero_idrometrico: number | null;
  soglia_allerta_gialla: number | null;
  soglia_allerta_arancione: number | null;
  soglia_allerta_rossa: number | null;
  fonte_dati: string;
  attiva: boolean;
  webcam_url?: string | null;
  regione_nome: string | null;
  bacino_nome: string | null;
  ultima_misurazione: UltimaMisurazione | null;
}

export interface GeoJSONPoint {
  type: 'Point';
  coordinates: [number, number]; // [lon, lat]
}

export interface StazioneFeature {
  type: 'Feature';
  id: number;
  geometry: GeoJSONPoint;
  properties: StazioneProperties;
}

export interface FeatureCollectionStazioni {
  type: 'FeatureCollection';
  features: StazioneFeature[];
  total_count: number;
}

export interface TimeSeriesDataPoint {
  timestamp: string;
  livello: number | null;
  portata: number | null;
  stato_allerta: AlertLevel;
}

export interface StationTimeSeries {
  stazione_id: number;
  codice_stazione: string;
  nome: string;
  fiume: string | null;
  regione: string | null;
  soglie: {
    gialla: number | null;
    arancione: number | null;
    rossa: number | null;
    zero_idrometrico: number | null;
  };
  stats: {
    min_livello: number | null;
    max_livello: number | null;
    avg_livello: number | null;
    current_livello: number | null;
    delta_livello_24h: number | null;
    trend: 'in_aumento' | 'in_calo' | 'stazionario';
  };
  serie_storica: TimeSeriesDataPoint[];
}

export interface RegioneSummary {
  id: number;
  codice_istat: string;
  nome: string;
  totale_stazioni: number;
  stazioni_in_allerta: number;
}

// --- River LineString GeoJSON Types ---

export interface RiverProperties {
  id: number;
  nome: string;
  lunghezza_km: number | null;
  bacino_nome: string | null;
  regioni_attraversate: string | null;
  stazioni_attive: number;
}

export interface GeoJSONLineString {
  type: 'LineString';
  coordinates: [number, number][]; // [[lon, lat], ...]
}

export interface RiverFeature {
  type: 'Feature';
  id: number;
  geometry: GeoJSONLineString;
  properties: RiverProperties;
}

export interface RiverFeatureCollection {
  type: 'FeatureCollection';
  features: RiverFeature[];
  total_count: number;
}

// --- Independent River Webcams Types ---

export type WebcamFeedType = 'jpeg_stream' | 'iframe' | 'link_esterno';

export interface WebcamFluvialeProperties {
  id: number;
  nome: string;
  corso_dacqua: string;
  localita: string;
  regione: string;
  tipo_feed: WebcamFeedType;
  url_feed: string | null;
  url_web: string;
  provider: string;
  descrizione: string | null;
  attiva: boolean;
}

export interface WebcamFeature {
  type: 'Feature';
  id: number;
  geometry: GeoJSONPoint;
  properties: WebcamFluvialeProperties;
}

export interface WebcamFeatureCollection {
  type: 'FeatureCollection';
  features: WebcamFeature[];
  total_count: number;
}

