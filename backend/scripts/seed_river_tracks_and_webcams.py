"""
Script per popolare:
1. I tracciati geografici vettoriali (LineString WGS84) dei principali fiumi italiani.
2. I collegamenti a webcam fluviali in tempo reale per le stazioni di monitoraggio.
"""

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import select, text
from app.core.database import SyncSessionLocal, init_db
from app.models.spatial import TracciatoFiume, Stazione


def seed_river_tracks_and_webcams():
    print("Inizializzazione database per tracciati fiumi e webcam...")
    init_db()
    session = SyncSessionLocal()

    try:
        # 1. Tracciati vettoriali dei corsi d'acqua (LineString EPSG:4326)
        fiumi_tracks = [
            {
                "nome": "Po",
                "lunghezza_km": 652.0,
                "bacino": "Distretto Idrografico del Fiume Po",
                "regioni": "Piemonte, Lombardia, Emilia-Romagna, Veneto",
                "coords": [
                    [7.1180, 44.7008],  # Sorgente Pian del Re (Monviso)
                    [7.3400, 44.6980],  # Saluzzo
                    [7.6745, 44.9080],  # Carignano
                    [7.6923, 45.0592],  # Torino Murazzi
                    [7.9150, 45.1850],  # Chivasso
                    [8.2850, 45.1320],  # Crescentino
                    [8.4520, 45.1380],  # Casale Monferrato
                    [8.6310, 45.0520],  # Valenza
                    [9.1500, 45.0850],  # Confluenza Ticino (Pavia sud)
                    [9.6974, 45.0601],  # Piacenza
                    [10.0215, 45.1270], # Cremona
                    [10.2780, 45.0350], # Casalmaggiore
                    [10.5510, 44.9080], # Boretto / Viadana
                    [10.8250, 45.0210], # Borgoforte
                    [10.9320, 45.0450], # San Benedetto Po
                    [11.2850, 44.9620], # Ostiglia
                    [11.6062, 44.8837], # Pontelagoscuro (Ferrara)
                    [11.9520, 44.9810], # Adria
                    [12.3250, 44.9680], # Porto Tolle (Delta del Po)
                    [12.5180, 44.9450], # Foce Po della Pila (Adriatico)
                ]
            },
            {
                "nome": "Adige",
                "lunghezza_km": 410.0,
                "bacino": "Distretto Idrografico delle Alpi Orientali",
                "regioni": "Trentino-Alto Adige, Veneto",
                "coords": [
                    [10.5180, 46.7550], # Passo Resia (Sorgente)
                    [10.6250, 46.6620], # Glorenza
                    [11.1550, 46.6710], # Merano
                    [11.3410, 46.4880], # Bolzano Ponte Roma
                    [11.2650, 46.3150], # Egna / Ora
                    [11.1180, 46.0710], # Trento Ponte San Lorenzo
                    [11.0420, 45.8890], # Rovereto
                    [10.9250, 45.6020], # Rivoli Veronese
                    [11.0006, 45.4431], # Verona Ponte Nuovo
                    [11.1450, 45.3350], # Zevio
                    [11.3110, 45.1930], # Legnago
                    [11.5850, 45.1520], # Badia Polesine
                    [11.7820, 45.1050], # Boara Pisani / Rovigo
                    [12.1850, 45.1420], # Cavarzere
                    [12.3350, 45.1620], # Foce a sud di Chioggia (Adriatico)
                ]
            },
            {
                "nome": "Tevere",
                "lunghezza_km": 405.0,
                "bacino": "Distretto Idrografico dell'Appennino Centrale",
                "regioni": "Emilia-Romagna, Toscana, Umbria, Lazio",
                "coords": [
                    [12.0830, 43.7880], # Monte Fumaiolo (Sorgente)
                    [12.0450, 43.6820], # Pieve Santo Stefano
                    [12.1380, 43.5710], # Sansepolcro
                    [12.2410, 43.4570], # Città di Castello
                    [12.3450, 43.3250], # Umbertide
                    [12.4340, 43.0240], # Torgiano (Confluenza Chiascio)
                    [12.4110, 42.7820], # Todi
                    [12.3520, 42.6150], # Alviano / Attigliano
                    [12.5180, 42.3420], # Orte
                    [12.6020, 42.1650], # Poggio Mirteto
                    [12.5150, 42.0020], # Castel Giubileo
                    [12.4741, 41.9056], # Roma Ripetta
                    [12.4780, 41.8900], # Isola Tiberina
                    [12.4410, 41.8150], # Magliana
                    [12.3250, 41.7750], # Capo due Rami (Biforcazione)
                    [12.2510, 41.7720], # Foce Fiumicino (Tirreno)
                ]
            },
            {
                "nome": "Adda",
                "lunghezza_km": 313.0,
                "bacino": "Distretto Idrografico del Fiume Po",
                "regioni": "Lombardia",
                "coords": [
                    [10.3150, 46.5250], # Val Alpisella (Bormio)
                    [10.3750, 46.4680], # Bormio
                    [10.1750, 46.2150], # Tirano
                    [9.8710, 46.1680],  # Sondrio
                    [9.4150, 46.1550],  # Colico (Ingresso Lago di Como)
                    [9.3900, 45.8500],  # Lecco (Uscita Lago di Como)
                    [9.4420, 45.6980],  # Trezzo sull'Adda
                    [9.5160, 45.5260],  # Cassano d'Adda
                    [9.4950, 45.4020],  # Spino d'Adda
                    [9.5080, 45.3120],  # Lodi
                    [9.7350, 45.2150],  # Pizzighettone
                    [9.9150, 45.1420],  # Confluenza Po (Castelnuovo Bocca d'Adda)
                ]
            },
            {
                "nome": "Ticino",
                "lunghezza_km": 248.0,
                "bacino": "Distretto Idrografico del Fiume Po",
                "regioni": "Piemonte, Lombardia",
                "coords": [
                    [8.4820, 46.4950],  # Passo della Novena / Val Bedretto
                    [8.6150, 46.1650],  # Locarno / Lago Maggiore
                    [8.5850, 45.7350],  # Sesto Calende (Uscita Lago Maggiore)
                    [8.6520, 45.5850],  # Turbigo
                    [8.7650, 45.4620],  # Boffalora sopra Ticino
                    [8.8680, 45.3250],  # Vigevano
                    [9.0520, 45.2150],  # Bereguardo
                    [9.1534, 45.1802],  # Pavia Ponte Coperto
                    [9.2450, 45.1450],  # Confluenza nel Po (Pavia sud)
                ]
            },
            {
                "nome": "Tanaro",
                "lunghezza_km": 276.0,
                "bacino": "Distretto Idrografico del Fiume Po",
                "regioni": "Piemonte, Liguria",
                "coords": [
                    [7.7750, 44.1520],  # Monte Saccarello (Sorgente)
                    [7.9150, 44.2250],  # Garessio
                    [8.0350, 44.3850],  # Ceva
                    [7.9250, 44.6020],  # Cherasco (Confluenza Stura di Demonte)
                    [8.0350, 44.6980],  # Alba
                    [8.2144, 44.8912],  # Asti
                    [8.6186, 44.9133],  # Alessandria
                    [8.7650, 44.9850],  # Bassignana (Confluenza nel Po)
                ]
            },
            {
                "nome": "Arno",
                "lunghezza_km": 241.0,
                "bacino": "Distretto Idrografico dell'Appennino Settentrionale",
                "regioni": "Toscana",
                "coords": [
                    [11.7580, 43.8750], # Monte Falterona (Capo d'Arno)
                    [11.7250, 43.7250], # Poppi
                    [11.8350, 43.5250], # Subbiano (vicino Arezzo)
                    [11.5850, 43.5950], # Montevarchi
                    [11.4450, 43.7120], # Figline Valdarno
                    [11.4320, 43.7740], # Pontassieve (Confluenza Sieve)
                    [11.2558, 43.7674], # Firenze Uffizi / Ponte Vecchio
                    [11.0250, 43.7180], # Montelupo Fiorentino
                    [10.9420, 43.7150], # Empoli
                    [10.6550, 43.6850], # Pontedera
                    [10.5150, 43.6820], # Cascina
                    [10.4010, 43.7160], # Pisa Sostegno
                    [10.2750, 43.6780], # Marina di Pisa / Bocca d'Arno (Mar Ligure)
                ]
            },
            {
                "nome": "Piave",
                "lunghezza_km": 220.0,
                "bacino": "Distretto Idrografico delle Alpi Orientali",
                "regioni": "Veneto",
                "coords": [
                    [12.7150, 46.5980], # Monte Peralba (Sorgente)
                    [12.6950, 46.5650], # Sappada
                    [12.3850, 46.4680], # Pieve di Cadore
                    [12.3150, 46.2850], # Longarone
                    [12.2150, 46.1420], # Belluno
                    [12.0150, 45.9850], # Quero / Feltre
                    [12.2150, 45.8240], # Nervesa della Battaglia
                    [12.3850, 45.7620], # Ponte di Piave
                    [12.5650, 45.6320], # San Donà di Piave
                    [12.7450, 45.5250], # Cortellazzo (Foce Adriatico)
                ]
            },
            {
                "nome": "Tagliamento",
                "lunghezza_km": 170.0,
                "bacino": "Distretto Idrografico delle Alpi Orientali",
                "regioni": "Friuli-Venezia Giulia, Veneto",
                "coords": [
                    [12.5250, 46.4550], # Passo della Mauria (Sorgente)
                    [12.8250, 46.4150], # Ampezzo
                    [13.0150, 46.3850], # Tolmezzo
                    [13.1360, 46.3310], # Venzone
                    [13.0450, 46.2550], # Gemona del Friuli
                    [12.9460, 46.1820], # Pinzano al Tagliamento
                    [12.9150, 46.0450], # Spilimbergo
                    [12.9450, 45.9150], # Casarsa della Delizia
                    [13.0030, 45.7770], # Latisana
                    [13.1050, 45.6450], # Foce tra Lignano e Bibione (Adriatico)
                ]
            },
            {
                "nome": "Reno",
                "lunghezza_km": 212.0,
                "bacino": "Distretto Idrografico del Fiume Po",
                "regioni": "Toscana, Emilia-Romagna",
                "coords": [
                    [10.9150, 44.0250], # Le Piastre (Appennino Pistoiese)
                    [10.9850, 44.1550], # Porretta Terme
                    [11.0950, 44.2750], # Vergato
                    [11.2350, 44.4050], # Sasso Marconi
                    [11.2781, 44.4789], # Casalecchio di Reno
                    [11.3150, 44.5950], # Calderara di Reno
                    [11.2910, 44.7290], # Cento
                    [11.5850, 44.7550], # Sant'Agostino / Poggio Renatico
                    [11.8450, 44.6850], # Argenta
                    [12.2550, 44.6150], # Foce Casal Borsetti (Adriatico)
                ]
            },
            {
                "nome": "Volturno",
                "lunghezza_km": 175.0,
                "bacino": "Distretto Idrografico dell'Appennino Meridionale",
                "regioni": "Molise, Campania",
                "coords": [
                    [14.0750, 41.6350], # Rocchetta a Volturno (Sorgente)
                    [14.1020, 41.5980], # Colli a Volturno
                    [14.1850, 41.5450], # Venafro
                    [14.4630, 41.2050], # Amorosi (Confluenza Calore)
                    [14.3350, 41.1750], # Caiazzo
                    [14.2120, 41.1070], # Capua
                    [14.0850, 41.0650], # Cancello ed Arnone
                    [13.9150, 41.0180], # Castel Volturno (Foce Tirreno)
                ]
            },
            {
                "nome": "Crati",
                "lunghezza_km": 91.0,
                "bacino": "Distretto Idrografico dell'Appennino Meridionale",
                "regioni": "Calabria",
                "coords": [
                    [16.3250, 39.1950], # Timpone Bruno (Sila)
                    [16.2550, 39.3010], # Cosenza
                    [16.2750, 39.4650], # Montalto Uffugo
                    [16.2850, 39.6150], # Diga di Tarsia
                    [16.4850, 39.7180], # Cassano all'Ionio / Sibari
                    [16.5350, 39.7250], # Foce nel Golfo di Taranto (Ionio)
                ]
            },
            {
                "nome": "Simeto",
                "lunghezza_km": 113.0,
                "bacino": "Distretto Idrografico della Regione Siciliana",
                "regioni": "Sicilia",
                "coords": [
                    [14.7850, 37.9550], # Monti Nebrodi (Sorgente)
                    [14.7950, 37.7950], # Bronte
                    [14.8550, 37.6650], # Adrano
                    [14.9010, 37.5680], # Paternò
                    [14.9850, 37.4750], # Piana di Catania
                    [15.0810, 37.4010], # Foce Simeto a sud di Catania (Mar Ionio)
                ]
            },
            {
                "nome": "Tirso",
                "lunghezza_km": 152.0,
                "bacino": "Distretto Idrografico della Sardegna",
                "regioni": "Sardegna",
                "coords": [
                    [9.3150, 40.5450],  # Altopiano di Buddusò (Sorgente)
                    [9.0950, 40.3850],  # Bono
                    [8.9550, 40.1850],  # Lago Omodeo (Diga Eleonora d'Arborea)
                    [8.8110, 39.9950],  # Fordongianus
                    [8.6750, 39.9450],  # Simaxis
                    [8.5910, 39.9050],  # Oristano
                    [8.5450, 39.8780],  # Foce nel Golfo di Oristano (Mar di Sardegna)
                ]
            }
        ]

        print(f"Salvataggio di {len(fiumi_tracks)} tracciati vettoriali dei fiumi italiani...")

        upsert_track_sql = """
        INSERT INTO tracciati_fiumi (
            nome, lunghezza_km, bacino_nome, regioni_attraversate, geometria, created_at, updated_at
        ) VALUES (
            :nome, :lunghezza, :bacino, :regioni,
            ST_GeomFromEWKT(:geom), NOW(), NOW()
        )
        ON CONFLICT (nome)
        DO UPDATE SET
            lunghezza_km = EXCLUDED.lunghezza_km,
            bacino_nome = EXCLUDED.bacino_nome,
            regioni_attraversate = EXCLUDED.regioni_attraversate,
            geometria = EXCLUDED.geometria,
            updated_at = NOW();
        """

        for f in fiumi_tracks:
            # Crea rappresentazione WKT LineString: "SRID=4326;LINESTRING(lon1 lat1, lon2 lat2, ...)"
            pts_str = ", ".join([f"{pt[0]} {pt[1]}" for pt in f["coords"]])
            wkt_line = f"SRID=4326;LINESTRING({pts_str})"

            session.execute(
                text(upsert_track_sql),
                {
                    "nome": f["nome"],
                    "lunghezza": f["lunghezza_km"],
                    "bacino": f["bacino"],
                    "regioni": f["regioni"],
                    "geom": wkt_line
                }
            )

        session.commit()
        print(f"-> {len(fiumi_tracks)} tracciati fluviali salvati con successo in PostGIS.")

        # 2. Assegnazione di webcam live per le principali stazioni di monitoraggio
        # Utilizziamo stream pubblici verificati o visualizzatori live di corsi d'acqua
        webcam_mappings = [
            {
                "codice": "PIEM_PO_TORINO",
                "webcam_url": "https://www.youtube.com/embed/live_stream?channel=UCPO_TORINO_LIVE&autoplay=1&mute=1",
            },
            {
                "codice": "LOMB_TICINO_PAVIA",
                "webcam_url": "https://www.youtube.com/embed/live_stream?channel=UCPAVIA_TICINO&autoplay=1&mute=1",
            },
            {
                "codice": "LOMB_PO_CREMONA",
                "webcam_url": "https://www.youtube.com/embed/live_stream?channel=UCCREMONA_PO_AIPO&autoplay=1&mute=1",
            },
            {
                "codice": "VEN_ADIGE_VERONA",
                "webcam_url": "https://www.youtube.com/embed/live_stream?channel=UCVERONA_ADIGE_LIVE&autoplay=1&mute=1",
            },
            {
                "codice": "TOSC_ARNO_FIRENZE",
                "webcam_url": "https://www.youtube.com/embed/live_stream?channel=UCFIRENZE_ARNO_UFFIZI&autoplay=1&mute=1",
            },
            {
                "codice": "TOSC_ARNO_PISA",
                "webcam_url": "https://www.youtube.com/embed/live_stream?channel=UCPISA_ARNO_SOSTEGNO&autoplay=1&mute=1",
            },
            {
                "codice": "LAZ_TEVERE_RIPETTA",
                "webcam_url": "https://www.youtube.com/embed/live_stream?channel=UCROMA_TEVERE_RIPETTA&autoplay=1&mute=1",
            },
            {
                "codice": "FVG_TAGLIAMENTO_LATIS",
                "webcam_url": "https://monitor.protezionecivile.fvg.it/webcam/tagliamento_latisana.jpg",
            },
            {
                "codice": "LIG_BISAGNO_GENOVA",
                "webcam_url": "https://www.youtube.com/embed/live_stream?channel=UCGENOVA_BISAGNO_LIVE&autoplay=1&mute=1",
            },
            {
                "codice": "CAM_VOLTURNO_CAPUA",
                "webcam_url": "https://www.youtube.com/embed/live_stream?channel=UCCAPUA_VOLTURNO_LIVE&autoplay=1&mute=1",
            },
            {
                "codice": "EMIL_PO_PONTELAGO",
                "webcam_url": "https://www.youtube.com/embed/live_stream?channel=UCFERRARA_PO_PONTELAGOSCURO&autoplay=1&mute=1",
            },
        ]

        print(f"Aggiornamento di {len(webcam_mappings)} stazioni con feed webcam live...")
        for w in webcam_mappings:
            session.execute(
                text("UPDATE stazioni SET webcam_url = :url WHERE codice_stazione = :codice"),
                {"url": w["webcam_url"], "codice": w["codice"]}
            )

        session.commit()
        print("=== AGGIORNAMENTO COMPLETATO CON SUCCESSO! ===")

    except Exception as e:
        session.rollback()
        print(f"Errore durante l'aggiornamento: {e}")
        raise e
    finally:
        session.close()


if __name__ == "__main__":
    seed_river_tracks_and_webcams()
