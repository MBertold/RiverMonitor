"""
Script di seeding per popolare il database con stazioni e serie temporali idrometriche realistiche.
Eseguibile sia da host che dentro il container backend:
    python backend/scripts/seed_demo_data.py
"""

import sys
import os
import random
from datetime import datetime, timedelta, timezone

# Aggiungi cartella root del backend al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import select, text
from geoalchemy2.elements import WKTElement
from app.core.database import sync_engine, SyncSessionLocal, init_db
from app.models.spatial import Regione, BacinoIdrografico, Stazione
from app.models.measurement import Misurazione


def run_seed():
    print("Inizializzazione database e PostGIS...")
    init_db()

    session = SyncSessionLocal()
    try:
        # 1. Regioni
        regioni_data = [
            {"codice_istat": "01", "nome": "Piemonte"},
            {"codice_istat": "03", "nome": "Lombardia"},
            {"codice_istat": "05", "nome": "Veneto"},
            {"codice_istat": "08", "nome": "Emilia-Romagna"},
            {"codice_istat": "09", "nome": "Toscana"},
            {"codice_istat": "12", "nome": "Lazio"},
        ]

        regioni_map = {}
        for r_dict in regioni_data:
            reg = session.scalar(select(Regione).where(Regione.codice_istat == r_dict["codice_istat"]))
            if not reg:
                reg = Regione(codice_istat=r_dict["codice_istat"], nome=r_dict["nome"])
                session.add(reg)
                session.flush()
            regioni_map[reg.nome] = reg

        print(f"Regioni censite: {len(regioni_map)}")

        # 2. Bacini Idrografici
        bacini_data = [
            {"codice": "PO", "nome": "Bacino Idrografico del Fiume Po", "autorita": "Autorità di Bacino Distrettuale del Fiume Po"},
            {"codice": "ADIGE", "nome": "Bacino Idrografico dell'Adige", "autorita": "Autorità di Bacino Alpi Orientali"},
            {"codice": "ARNO", "nome": "Bacino Idrografico dell'Arno", "autorita": "Autorità di Bacino Appennino Settentrionale"},
            {"codice": "TEVERE", "nome": "Bacino Idrografico del Tevere", "autorita": "Autorità di Bacino Appennino Centrale"},
        ]

        bacini_map = {}
        for b_dict in bacini_data:
            bac = session.scalar(select(BacinoIdrografico).where(BacinoIdrografico.codice == b_dict["codice"]))
            if not bac:
                bac = BacinoIdrografico(
                    codice=b_dict["codice"],
                    nome=b_dict["nome"],
                    autorita_distretto=b_dict["autorita"]
                )
                session.add(bac)
                session.flush()
            bacini_map[bac.codice] = bac

        print(f"Bacini censiti: {len(bacini_map)}")

        # 3. Stazioni Idrometriche
        stazioni_data = [
            {
                "codice": "PIEM_PO_TORINO",
                "nome": "Po a Torino - Murazzi",
                "fiume": "Po",
                "regione": "Piemonte",
                "bacino": "PO",
                "lon": 7.6923,
                "lat": 45.0592,
                "quota_zero": 215.4,
                "soglia_gialla": 3.5,
                "soglia_arancione": 4.5,
                "soglia_rossa": 5.5,
                "fonte": "ARPA Piemonte",
                "scenario": "giallo"  # livello simulato che tocca soglia gialla
            },
            {
                "codice": "PIEM_TANARO_ALESS",
                "nome": "Tanaro ad Alessandria",
                "fiume": "Tanaro",
                "regione": "Piemonte",
                "bacino": "PO",
                "lon": 8.6186,
                "lat": 44.9133,
                "quota_zero": 88.2,
                "soglia_gialla": 4.0,
                "soglia_arancione": 5.2,
                "soglia_rossa": 6.5,
                "fonte": "ARPA Piemonte",
                "scenario": "verde"
            },
            {
                "codice": "LOMB_TICINO_PAVIA",
                "nome": "Ticino a Pavia - Ponte Coperto",
                "fiume": "Ticino",
                "regione": "Lombardia",
                "bacino": "PO",
                "lon": 9.1534,
                "lat": 45.1802,
                "quota_zero": 69.5,
                "soglia_gialla": 2.2,
                "soglia_arancione": 3.0,
                "soglia_rossa": 3.8,
                "fonte": "ARPA Lombardia",
                "scenario": "arancione"  # tocca soglia arancione
            },
            {
                "codice": "EMIL_PO_PIACENZA",
                "nome": "Po a Piacenza",
                "fiume": "Po",
                "regione": "Emilia-Romagna",
                "bacino": "PO",
                "lon": 9.6974,
                "lat": 45.0601,
                "quota_zero": 48.0,
                "soglia_gialla": 5.0,
                "soglia_arancione": 6.5,
                "soglia_rossa": 8.0,
                "fonte": "ARPAE Emilia-Romagna",
                "scenario": "verde"
            },
            {
                "codice": "EMIL_PO_PONTELAGO",
                "nome": "Po a Pontelagoscuro (Ferrara)",
                "fiume": "Po",
                "regione": "Emilia-Romagna",
                "bacino": "PO",
                "lon": 11.6062,
                "lat": 44.8837,
                "quota_zero": 8.5,
                "soglia_gialla": 1.5,
                "soglia_arancione": 2.5,
                "soglia_rossa": 3.5,
                "fonte": "ARPAE Emilia-Romagna",
                "scenario": "rosso"  # situazione di piena / allerta rossa
            },
            {
                "codice": "VEN_ADIGE_VERONA",
                "nome": "Adige a Verona - Ponte Nuovo",
                "fiume": "Adige",
                "regione": "Veneto",
                "bacino": "ADIGE",
                "lon": 11.0006,
                "lat": 45.4431,
                "quota_zero": 45.1,
                "soglia_gialla": 1.8,
                "soglia_arancione": 2.8,
                "soglia_rossa": 3.8,
                "fonte": "ARPAV Veneto",
                "scenario": "verde"
            },
            {
                "codice": "TOSC_ARNO_FIRENZE",
                "nome": "Arno a Firenze - Uffizi",
                "fiume": "Arno",
                "regione": "Toscana",
                "bacino": "ARNO",
                "lon": 11.2558,
                "lat": 43.7674,
                "quota_zero": 42.0,
                "soglia_gialla": 3.0,
                "soglia_arancione": 4.5,
                "soglia_rossa": 5.5,
                "fonte": "CFR Toscana",
                "scenario": "giallo"
            },
            {
                "codice": "LAZ_TEVERE_RIPETTA",
                "nome": "Tevere a Roma - Ripetta",
                "fiume": "Tevere",
                "regione": "Lazio",
                "bacino": "TEVERE",
                "lon": 12.4741,
                "lat": 41.9056,
                "quota_zero": 5.2,
                "soglia_gialla": 7.0,
                "soglia_arancione": 9.5,
                "soglia_rossa": 12.0,
                "fonte": "Protezione Civile Lazio",
                "scenario": "verde"
            },
        ]

        stazioni_db = []
        for s_info in stazioni_data:
            staz = session.scalar(select(Stazione).where(Stazione.codice_stazione == s_info["codice"]))
            point_wkt = f"SRID=4326;POINT({s_info['lon']} {s_info['lat']})"
            
            if not staz:
                staz = Stazione(
                    codice_stazione=s_info["codice"],
                    nome=s_info["nome"],
                    fiume=s_info["fiume"],
                    regione_id=regioni_map[s_info["regione"]].id if s_info["regione"] in regioni_map else None,
                    bacino_id=bacini_map[s_info["bacino"]].id if s_info["bacino"] in bacini_map else None,
                    posizione=point_wkt,
                    quota_zero_idrometrico=s_info["quota_zero"],
                    soglia_allerta_gialla=s_info["soglia_gialla"],
                    soglia_allerta_arancione=s_info["soglia_arancione"],
                    soglia_allerta_rossa=s_info["soglia_rossa"],
                    fonte_dati=s_info["fonte"],
                    attiva=True
                )
                session.add(staz)
                session.flush()
            stazioni_db.append((staz, s_info["scenario"]))

        print(f"Stazioni idrometriche create/aggiornate: {len(stazioni_db)}")

        # 4. Generazione serie temporali (Ultime 48 ore a intervalli di 1 ora)
        now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        total_meas = 0

        for staz, scenario in stazioni_db:
            base_gialla = staz.soglia_allerta_gialla or 2.0
            base_arancione = staz.soglia_allerta_arancione or 3.5
            base_rossa = staz.soglia_allerta_rossa or 5.0

            # Calcolo target medio in base allo scenario
            if scenario == "rosso":
                target_peak = base_rossa + 0.3
            elif scenario == "arancione":
                target_peak = base_arancione + 0.2
            elif scenario == "giallo":
                target_peak = base_gialla + 0.2
            else:
                target_peak = base_gialla * 0.55

            # Curva idrografica sintetica
            for h in range(48, -1, -1):
                t = now - timedelta(hours=h)
                
                # Variazione sinusoidale con rumore per simulare l'onda di piena o andamento ordinario
                cycle = (48 - h) / 48.0 * 3.14159
                variation = random.uniform(-0.08, 0.08)
                livello = round(max(0.1, target_peak * (0.7 + 0.3 * (1 - abs(24 - h) / 24.0)) + variation), 2)
                portata = round(livello * random.uniform(80.0, 150.0), 1)

                # Stato allerta
                if staz.soglia_allerta_rossa and livello >= staz.soglia_allerta_rossa:
                    stato = "rosso"
                elif staz.soglia_allerta_arancione and livello >= staz.soglia_allerta_arancione:
                    stato = "arancione"
                elif staz.soglia_allerta_gialla and livello >= staz.soglia_allerta_gialla:
                    stato = "giallo"
                else:
                    stato = "verde"

                # Upsert misurazione
                session.execute(
                    text("""
                    INSERT INTO misurazioni (stazione_id, timestamp, livello_idrometrico, portata, stato_allerta, validato, created_at)
                    VALUES (:stazione_id, :timestamp, :livello, :portata, :stato, true, NOW())
                    ON CONFLICT (stazione_id, timestamp)
                    DO UPDATE SET livello_idrometrico = EXCLUDED.livello_idrometrico, portata = EXCLUDED.portata, stato_allerta = EXCLUDED.stato_allerta;
                    """),
                    {
                        "stazione_id": staz.id,
                        "timestamp": t,
                        "livello": livello,
                        "portata": portata,
                        "stato": stato
                    }
                )
                total_meas += 1

        session.commit()
        print(f"Serie temporali generate con successo: {total_meas} misurazioni salvate.")

    except Exception as exc:
        session.rollback()
        print(f"Errore durante il seeding: {exc}")
        raise exc
    finally:
        session.close()


if __name__ == "__main__":
    run_seed()
