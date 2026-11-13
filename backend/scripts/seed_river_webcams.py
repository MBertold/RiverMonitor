"""
Script per popolare il layer dedicato 'Webcam Fluviali & Ponti':
Punti di osservazione video indipendenti sui fiumi italiani (feed JPEG diretti e webcam panoramiche).
"""

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import text
from app.core.database import SyncSessionLocal, init_db


def seed_river_webcams():
    print("Inizializzazione database per layer webcam fluviali...")
    init_db()
    session = SyncSessionLocal()

    try:
        # 1. Pulisce i vecchi link placeholder non funzionanti dalle stazioni idrometriche
        print("Ripristino campo webcam_url nelle stazioni idrometriche...")
        session.execute(text("UPDATE stazioni SET webcam_url = NULL;"))

        # 2. Elenco webcam fluviali indipendenti verificate e panoramiche
        webcams = [
            {
                "nome": "Fiume Po a Boretto - Lido Po & Porto Turistico",
                "corso_dacqua": "Po",
                "localita": "Boretto (RE)",
                "regione": "Emilia-Romagna",
                "tipo_feed": "jpeg_stream",
                "url_feed": "https://www.reggioemiliameteo.it/webcam/boretto/boretto.jpg",
                "url_web": "https://www.reggioemiliameteo.it/webcam-fiume-po-boretto.php",
                "provider": "Reggio Emilia Meteo",
                "descrizione": "Webcam storica in live streaming ad alta risoluzione puntata sul Porto Turistico di Boretto per il controllo costante di piene e secche del Po.",
                "lon": 10.5528,
                "lat": 44.9075,
            },
            {
                "nome": "Fiume Brenta a Bassano del Grappa - Ponte degli Alpini",
                "corso_dacqua": "Brenta",
                "localita": "Bassano del Grappa (VI)",
                "regione": "Veneto",
                "tipo_feed": "jpeg_stream",
                "url_feed": "http://servizi.comune.bassano.vi.it/webcamponte/snap_ponte.jpg",
                "url_web": "https://www.comune.bassano.vi.it/",
                "provider": "Comune di Bassano del Grappa",
                "descrizione": "Telecamera municipale civica in tempo reale puntata sullo storico Ponte Vecchio e sul flusso del fiume Brenta in uscita dalle Prealpi.",
                "lon": 11.7336,
                "lat": 45.7673,
            },
            {
                "nome": "Fiume Trebbia a Gorreto - Val Trebbia",
                "corso_dacqua": "Trebbia",
                "localita": "Gorreto (GE)",
                "regione": "Liguria",
                "tipo_feed": "jpeg_stream",
                "url_feed": "https://www.tripwebcam.com/webcam-live/gorreto-trebbia/cam.jpg",
                "url_web": "https://turbolic.limet.cloud/",
                "provider": "Limet / TripWebcam",
                "descrizione": "Webcam ad alta definizione puntata direttamente sul greto e sulle acque cristalline del Fiume Trebbia nell'Appennino Ligure-Emiliano.",
                "lon": 9.2974,
                "lat": 44.6044,
            },
            {
                "nome": "Torrente Dolo a Civago - Parco Appennino Tosco-Emiliano",
                "corso_dacqua": "Dolo",
                "localita": "Civago, Villa Minozzo (RE)",
                "regione": "Emilia-Romagna",
                "tipo_feed": "jpeg_stream",
                "url_feed": "https://www.reggioemiliameteo.it/webcam/civago/civago.jpg",
                "url_web": "https://www.reggioemiliameteo.it/webcam-civago-ponte-dolo.php",
                "provider": "Reggio Emilia Meteo",
                "descrizione": "Inquadratura del ponte sul torrente montano Dolo, affluente del Secchia, per il monitoraggio idrologico di quota.",
                "lon": 10.4350,
                "lat": 44.2758,
            },
            {
                "nome": "Fiume Arno a Firenze - Ponte Vecchio",
                "corso_dacqua": "Arno",
                "localita": "Firenze",
                "regione": "Toscana",
                "tipo_feed": "link_esterno",
                "url_feed": None,
                "url_web": "https://www.skylinewebcams.com/it/webcam/italia/toscana/firenze/ponte-vecchio.html",
                "provider": "SkylineWebcams",
                "descrizione": "Spettacolare inquadratura 24/7 di Ponte Vecchio e delle arcate sull'Arno da Palazzo degli Uffizi e Lungarno degli Archibusieri.",
                "lon": 11.2531,
                "lat": 43.7680,
            },
            {
                "nome": "Fiume Adige a Verona - Ponte di Castelvecchio",
                "corso_dacqua": "Adige",
                "localita": "Verona",
                "regione": "Veneto",
                "tipo_feed": "link_esterno",
                "url_feed": None,
                "url_web": "https://www.skylinewebcams.com/it/webcam/italia/veneto/verona/verona-ponte-di-castelvecchio.html",
                "provider": "SkylineWebcams",
                "descrizione": "Veduta panoramica in diretta del ponte scaligero fortificato medievale e della grande ansa del fiume Adige a Verona.",
                "lon": 10.9877,
                "lat": 45.4398,
            },
            {
                "nome": "Canal Grande a Venezia - Ponte di Rialto",
                "corso_dacqua": "Canal Grande",
                "localita": "Venezia",
                "regione": "Veneto",
                "tipo_feed": "link_esterno",
                "url_feed": None,
                "url_web": "https://www.skylinewebcams.com/it/webcam/italia/veneto/venezia/venezia-ponte-di-rialto.html",
                "provider": "SkylineWebcams",
                "descrizione": "Inquadratura sul principale canale d'acqua veneziano e il transito delle imbarcazioni ai piedi del Ponte di Rialto.",
                "lon": 12.3359,
                "lat": 45.4380,
            },
            {
                "nome": "Fiume Tevere a Roma - Ponte Sisto & Trastevere",
                "corso_dacqua": "Tevere",
                "localita": "Roma",
                "regione": "Lazio",
                "tipo_feed": "link_esterno",
                "url_feed": None,
                "url_web": "https://www.skylinewebcams.com/it/webcam/italia/lazio/roma/ponte-sisto-trastevere.html",
                "provider": "SkylineWebcams",
                "descrizione": "Vista panoramica sul Tevere dal Lungotevere dei Tebaldi verso Ponte Sisto e il rione Trastevere.",
                "lon": 12.4708,
                "lat": 41.8922,
            },
            {
                "nome": "Fiume Ticino a Pavia - Ponte Coperto & Lungoticino",
                "corso_dacqua": "Ticino",
                "localita": "Pavia",
                "regione": "Lombardia",
                "tipo_feed": "link_esterno",
                "url_feed": None,
                "url_web": "https://www.battelliericolombo.it/",
                "provider": "Battellieri Colombo",
                "descrizione": "Postazione di osservazione installata sulla casa galleggiante dei Battellieri Colombo affacciata sul Ponte Coperto di Pavia.",
                "lon": 9.1539,
                "lat": 45.1806,
            },
            {
                "nome": "Foce dell'Arno a Marina di Pisa - Bocca d'Arno",
                "corso_dacqua": "Arno",
                "localita": "Marina di Pisa (PI)",
                "regione": "Toscana",
                "tipo_feed": "link_esterno",
                "url_feed": None,
                "url_web": "https://www.meteotoscana.it/webcam/marina-di-pisa-bocca-d-arno/",
                "provider": "Meteo Toscana",
                "descrizione": "Inquadratura del tratto terminale e della foce del Fiume Arno con i tradizionali retoni da pesca (refe/bilancioni).",
                "lon": 10.2764,
                "lat": 43.6806,
            },
            {
                "nome": "Fiume Sarca a Torbole sul Garda - Foce nel Lago",
                "corso_dacqua": "Sarca",
                "localita": "Nago-Torbole (TN)",
                "regione": "Trentino-Alto Adige",
                "tipo_feed": "link_esterno",
                "url_feed": None,
                "url_web": "https://www.windy.com/webcams/",
                "provider": "Circolo Vela Torbole / Windy",
                "descrizione": "Telecamera panoramica sul delta del fiume Sarca che immette le acque alpine nel Lago di Garda settentrionale.",
                "lon": 10.8719,
                "lat": 45.8712,
            },
        ]

        # 3. Pulizia e inserimento webcam fluviali
        session.execute(text("TRUNCATE TABLE webcam_fluviali RESTART IDENTITY;"))

        insert_sql = """
        INSERT INTO webcam_fluviali (
            nome, corso_dacqua, localita, regione, tipo_feed, url_feed, url_web, provider, descrizione, attiva, posizione, created_at, updated_at
        ) VALUES (
            :nome, :corso_dacqua, :localita, :regione, :tipo_feed, :url_feed, :url_web, :provider, :descrizione, true,
            ST_SetSRID(ST_MakePoint(:lon, :lat), 4326), NOW(), NOW()
        );
        """

        for w in webcams:
            session.execute(text(insert_sql), w)

        session.commit()
        print(f"-> Inserite con successo {len(webcams)} webcam fluviali indipendenti in PostGIS.")

    except Exception as e:
        session.rollback()
        print(f"Errore durante l'inserimento: {e}")
        raise e
    finally:
        session.close()


if __name__ == "__main__":
    seed_river_webcams()
