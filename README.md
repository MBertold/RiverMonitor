# RiverMonitor 🌊🇮🇹

Piattaforma web full-stack per il monitoraggio idrometrico in tempo reale dei fiumi italiani. Raccoglie dati frammentati su base regionale (ARPA, Protezione Civile, PDND), li normalizza e li espone tramite API RESTful / GeoJSON e mappa interattiva.

---

## 🏛️ Architettura dei Microservizi

L'infrastruttura è completamente containerizzata con **Docker Compose**:

1. **Database Spaziale (`db`)**: PostgreSQL 16 con estensione PostGIS 3.4. Schema a stella ottimizzato per GIS e serie temporali.
2. **Backend API (`backend`)**: Python con FastAPI e SQLAlchemy 2.0. Espone endpoint RESTful ad alte prestazioni, GeoJSON (RFC 7946) e serie storiche.
3. **ETL Worker (`etl-worker`)**: Servizio worker Python asincrono che estrae dati dagli enti regionali (es. ARPA Piemonte, ARPAE), normalizza i dati ed esegue **upsert idempotenti**.
4. **Frontend & Reverse Proxy (`frontend`)**: Single Page Application in React (Vite + TypeScript + Tailwind CSS + Leaflet + TanStack Query + Recharts) servita tramite Nginx che funge anche da reverse proxy per le API.

---

## 🗺️ Endpoint API Chiave (FastAPI)

* `GET /api/v1/stations`: Restituisce le stazioni idrometriche in formato **GeoJSON FeatureCollection** (compatibile con Leaflet, MapLibre, QGIS).
  * Filtri query: `regione_id`, `codice_istat`, `fiume`, `stato_allerta` (verde, giallo, arancione, rosso), `bbox` (min_lon,min_lat,max_lon,max_lat).
* `GET /api/v1/stations/{id}`: Dettaglio proprietà e ultima misurazione della singola stazione.
* `GET /api/v1/stations/{id}/measurements?hours=48`: Serie storica cronologica delle ultime 24/48 ore con soglie di allerta (gialla, arancione, rossa) e statistiche (min, max, media, variazione 24h, trend).
* `POST /api/v1/measurements/batch`: Endpoint di caricamento massivo per i worker ETL (upsert nativo su database).
* `GET /api/v1/regions`: Elenco regioni con contatore stazioni e stato di allerta.

---

## 🚀 Avvio del Sistema

### 1. Avvio con Docker Compose (consigliato)

```bash
# Avvia l'intero stack (DB, Backend, ETL, Frontend/Nginx)
docker compose up --build -d
```

* **Frontend & Mappa**: [http://localhost](http://localhost)
* **FastAPI Docs (Swagger UI)**: [http://localhost/docs](http://localhost/docs) o [http://localhost:8000/docs](http://localhost:8000/docs)
* **Healthcheck PostGIS**: [http://localhost/api/v1/health](http://localhost:8000/health)

### 2. Popolamento Dati Dimostrativi (Seed)

Per caricare stazioni idrometriche reali (Po, Tanaro, Ticino, Adige, Arno, Tevere) e 48 ore di serie storiche:

```bash
docker compose exec backend python scripts/seed_demo_data.py
```

### 3. Sviluppo Locale Frontend (opzionale con Hot Reload)

```bash
cd frontend
npm install
npm run dev
# Mappa disponibile su http://localhost:5173 con proxy automatico verso FastAPI
```
