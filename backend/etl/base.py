import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger("rivermonitor.etl")


class BaseRegionalConnector(ABC):
    """
    Classe base per tutti i connettori regionali (ARPA, Protezione Civile, PDND).
    Ogni connettore gestisce l'estrazione specifica dell'ente, la normalizzazione
    e l'upsert atomico su PostgreSQL + PostGIS.
    """

    def __init__(self, name: str, region_name: str, istat_code: str):
        self.name = name
        self.region_name = region_name
        self.istat_code = istat_code

    @abstractmethod
    def fetch_raw_data(self) -> Any:
        """Estrae i dati grezzi (API REST, CSV, JSON, o endpoint WFS)."""
        pass

    @abstractmethod
    def normalize(self, raw_data: Any) -> List[Dict[str, Any]]:
        """
        Normalizza i dati nel formato standard per RiverMonitor:
        [
            {
                "codice_stazione": "...",
                "nome_stazione": "...",
                "fiume": "...",
                "lat": 45.0,
                "lon": 7.5,
                "timestamp": datetime(...),
                "livello_idrometrico": 2.15,
                "portata": 450.0,
                "soglia_gialla": 3.0,
                "soglia_arancione": 4.5,
                "soglia_rossa": 5.5,
            },
            ...
        ]
        """
        pass

    def load(self, records: List[Dict[str, Any]], session: Session) -> Dict[str, int]:
        """
        Carica i dati su PostGIS:
        1. Anagrafica stazioni: inserisce o aggiorna metadati e posizione geografica.
        2. Misurazioni temporali: upsert idempotente su (stazione_id, timestamp).
        """
        if not records:
            logger.info(f"[{self.name}] Nessun record da caricare.")
            return {"stations_synced": 0, "measurements_upserted": 0}

        # 1. Recupera ID regione
        reg_id = session.execute(
            text("SELECT id FROM regioni WHERE codice_istat = :istat"),
            {"istat": self.istat_code}
        ).scalar()

        if not reg_id:
            reg_id = session.execute(
                text("INSERT INTO regioni (codice_istat, nome, created_at, updated_at) VALUES (:istat, :nome, NOW(), NOW()) RETURNING id"),
                {"istat": self.istat_code, "nome": self.region_name}
            ).scalar()

        # 2. Sync anagrafica stazioni
        stazioni_upsert_sql = """
        INSERT INTO stazioni (
            codice_stazione, nome, fiume, regione_id, posizione,
            soglia_allerta_gialla, soglia_allerta_arancione, soglia_allerta_rossa,
            fonte_dati, attiva, created_at, updated_at
        ) VALUES (
            :codice, :nome, :fiume, :regione_id,
            ST_SetSRID(ST_MakePoint(:lon, :lat), 4326),
            :soglia_gialla, :soglia_arancione, :soglia_rossa,
            :fonte, true, NOW(), NOW()
        )
        ON CONFLICT (codice_stazione)
        DO UPDATE SET
            nome = EXCLUDED.nome,
            fiume = COALESCE(EXCLUDED.fiume, stazioni.fiume),
            soglia_allerta_gialla = COALESCE(EXCLUDED.soglia_allerta_gialla, stazioni.soglia_allerta_gialla),
            soglia_allerta_arancione = COALESCE(EXCLUDED.soglia_allerta_arancione, stazioni.soglia_allerta_arancione),
            soglia_allerta_rossa = COALESCE(EXCLUDED.soglia_allerta_rossa, stazioni.soglia_allerta_rossa),
            updated_at = NOW()
        RETURNING id, codice_stazione;
        """

        unique_stations = {}
        for r in records:
            codice = r["codice_stazione"]
            if codice not in unique_stations and "lat" in r and "lon" in r:
                unique_stations[codice] = r

        codice_to_id = {}
        for s in unique_stations.values():
            res = session.execute(
                text(stazioni_upsert_sql),
                {
                    "codice": s["codice_stazione"],
                    "nome": s["nome_stazione"],
                    "fiume": s.get("fiume"),
                    "regione_id": reg_id,
                    "lon": s["lon"],
                    "lat": s["lat"],
                    "soglia_gialla": s.get("soglia_gialla"),
                    "soglia_arancione": s.get("soglia_arancione"),
                    "soglia_rossa": s.get("soglia_rossa"),
                    "fonte": self.name
                }
            )
            row = res.mappings().first()
            if row:
                codice_to_id[row["codice_stazione"]] = row["id"]

        # Se alcune stazioni erano già presenti, recupera i loro ID
        missing_codici = [r["codice_stazione"] for r in records if r["codice_stazione"] not in codice_to_id]
        if missing_codici:
            existing = session.execute(
                text("SELECT id, codice_stazione FROM stazioni WHERE codice_stazione = ANY(:codici)"),
                {"codici": list(set(missing_codici))}
            ).mappings().all()
            for row in existing:
                codice_to_id[row["codice_stazione"]] = row["id"]

        # 3. Upsert serie temporale misurazioni
        meas_upsert_sql = """
        INSERT INTO misurazioni (
            stazione_id, timestamp, livello_idrometrico, portata, stato_allerta, validato, created_at
        ) VALUES (
            :stazione_id, :timestamp, :livello, :portata, :stato_allerta, :validato, NOW()
        )
        ON CONFLICT (stazione_id, timestamp)
        DO UPDATE SET
            livello_idrometrico = EXCLUDED.livello_idrometrico,
            portata = EXCLUDED.portata,
            stato_allerta = EXCLUDED.stato_allerta,
            validato = EXCLUDED.validato;
        """

        meas_count = 0
        for r in records:
            st_id = codice_to_id.get(r["codice_stazione"])
            if not st_id or r.get("timestamp") is None:
                continue

            livello = r.get("livello_idrometrico")
            stato = "verde"
            if livello is not None:
                if r.get("soglia_rossa") and livello >= r["soglia_rossa"]:
                    stato = "rosso"
                elif r.get("soglia_arancione") and livello >= r["soglia_arancione"]:
                    stato = "arancione"
                elif r.get("soglia_gialla") and livello >= r["soglia_gialla"]:
                    stato = "giallo"

            session.execute(
                text(meas_upsert_sql),
                {
                    "stazione_id": st_id,
                    "timestamp": r["timestamp"],
                    "livello": livello,
                    "portata": r.get("portata"),
                    "stato_allerta": stato,
                    "validato": r.get("validato", False)
                }
            )
            meas_count += 1

        session.commit()
        return {
            "stations_synced": len(unique_stations),
            "measurements_upserted": meas_count
        }

    def run(self, session: Session) -> Dict[str, Any]:
        """Esegue il ciclo completo ETL: Estrazione -> Normalizzazione -> Caricamento."""
        logger.info(f"Avvio ciclo ETL per [{self.name}] ({self.region_name})...")
        try:
            raw = self.fetch_raw_data()
            normalized = self.normalize(raw)
            result = self.load(normalized, session)
            logger.info(
                f"Completato ETL [{self.name}]: {result['stations_synced']} stazioni sincronizzate, "
                f"{result['measurements_upserted']} misurazioni caricate."
            )
            return {"status": "success", **result}
        except Exception as e:
            session.rollback()
            logger.error(f"Errore durante l'esecuzione dell'ETL per [{self.name}]: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}
