import sys
import os
import time
import signal
import logging
import argparse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import SyncSessionLocal, init_db
from etl.connectors.arpa_piemonte import ArpaPiemonteConnector
from etl.connectors.arpa_emilia_romagna import ArpaEmiliaRomagnaConnector

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [ETL Worker] %(message)s"
)
logger = logging.getLogger("rivermonitor.etl.worker")

RUNNING = True


def handle_shutdown(signum, frame):
    global RUNNING
    logger.info("Segnale di terminazione ricevuto. Chiusura aggraziata del worker ETL...")
    RUNNING = False


signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGTERM, handle_shutdown)


def run_etl_cycle():
    """Esegue un ciclo completo di ingestione su tutti i connettori regionali abilitati."""
    logger.info("--- Inizio ciclo di sincronizzazione ETL ---")
    
    # Inizializza DB e tabelle se necessario
    init_db()

    connectors = [
        ArpaPiemonteConnector(),
        ArpaEmiliaRomagnaConnector(),
    ]

    total_synced_stations = 0
    total_upserted_meas = 0

    session = SyncSessionLocal()
    try:
        for connector in connectors:
            res = connector.run(session)
            if res.get("status") == "success":
                total_synced_stations += res.get("stations_synced", 0)
                total_upserted_meas += res.get("measurements_upserted", 0)

        logger.info(
            f"--- Fine ciclo ETL: {total_synced_stations} stazioni attive, "
            f"{total_upserted_meas} nuove misurazioni salvate ---"
        )
    finally:
        session.close()


def main():
    parser = argparse.ArgumentParser(description="RiverMonitor ETL Worker")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Esegue una sola iterazione di sincronizzazione e termina"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=int(os.getenv("ETL_INTERVAL_SECONDS", "900")),
        help="Intervallo di polling in secondi (default: 900s / 15 minuti)"
    )
    args = parser.parse_args()

    if args.once:
        run_etl_cycle()
        return

    logger.info(f"Avvio ETL Worker in modalità continua (intervallo: {args.interval}s)...")
    while RUNNING:
        try:
            run_etl_cycle()
        except Exception as exc:
            logger.error(f"Eccezione imprevista nel worker ETL: {exc}", exc_info=True)

        # Attesa con risveglio immediato se arriva un segnale
        for _ in range(args.interval):
            if not RUNNING:
                break
            time.sleep(1)

    logger.info("Worker ETL terminato.")


if __name__ == "__main__":
    main()
