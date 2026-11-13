"""
Script completo per popolare l'anagrafica idrometrica nazionale con tutti i principali
fiumi e corsi d'acqua di tutte le 20 Regioni Italiane e i rispettivi distretti idrografici.
"""

import sys
import os
import random
from datetime import datetime, timedelta, timezone

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import select, text
from app.core.database import SyncSessionLocal, init_db
from app.models.spatial import Regione, BacinoIdrografico, Stazione


def seed_all_italian_rivers():
    print("Inizializzazione database...")
    init_db()
    session = SyncSessionLocal()

    try:
        # 1. Censimento di tutte le 20 Regioni Italiane con codice ISTAT
        regioni_data = [
            {"codice_istat": "01", "nome": "Piemonte"},
            {"codice_istat": "02", "nome": "Valle d'Aosta"},
            {"codice_istat": "03", "nome": "Lombardia"},
            {"codice_istat": "04", "nome": "Trentino-Alto Adige"},
            {"codice_istat": "05", "nome": "Veneto"},
            {"codice_istat": "06", "nome": "Friuli-Venezia Giulia"},
            {"codice_istat": "07", "nome": "Liguria"},
            {"codice_istat": "08", "nome": "Emilia-Romagna"},
            {"codice_istat": "09", "nome": "Toscana"},
            {"codice_istat": "10", "nome": "Umbria"},
            {"codice_istat": "11", "nome": "Marche"},
            {"codice_istat": "12", "nome": "Lazio"},
            {"codice_istat": "13", "nome": "Abruzzo"},
            {"codice_istat": "14", "nome": "Molise"},
            {"codice_istat": "15", "nome": "Campania"},
            {"codice_istat": "16", "nome": "Puglia"},
            {"codice_istat": "17", "nome": "Basilicata"},
            {"codice_istat": "18", "nome": "Calabria"},
            {"codice_istat": "19", "nome": "Sicilia"},
            {"codice_istat": "20", "nome": "Sardegna"},
        ]

        regioni_map = {}
        for r in regioni_data:
            reg = session.scalar(select(Regione).where(Regione.codice_istat == r["codice_istat"]))
            if not reg:
                reg = Regione(codice_istat=r["codice_istat"], nome=r["nome"])
                session.add(reg)
                session.flush()
            regioni_map[reg.nome] = reg

        print(f"-> Regioni sincronizzate: {len(regioni_map)}/20")

        # 2. Censimento delle Autorità di Bacino Distrettuali Italiane (D.Lgs 152/2006)
        bacini_data = [
            {"codice": "PO", "nome": "Distretto Idrografico del Fiume Po", "autorita": "Autorità di Bacino Distrettuale del Fiume Po"},
            {"codice": "ALPI_ORIENTALI", "nome": "Distretto Idrografico delle Alpi Orientali", "autorita": "Autorità di Bacino Alpi Orientali"},
            {"codice": "APPENNINO_SETT", "nome": "Distretto Idrografico dell'Appennino Settentrionale", "autorita": "Autorità di Bacino Appennino Settentrionale"},
            {"codice": "APPENNINO_CENT", "nome": "Distretto Idrografico dell'Appennino Centrale", "autorita": "Autorità di Bacino Appennino Centrale"},
            {"codice": "APPENNINO_MERID", "nome": "Distretto Idrografico dell'Appennino Meridionale", "autorita": "Autorità di Bacino Appennino Meridionale"},
            {"codice": "SICILIA", "nome": "Distretto Idrografico della Regione Siciliana", "autorita": "Regione Siciliana - Dipartimento Acque"},
            {"codice": "SARDEGNA", "nome": "Distretto Idrografico della Sardegna", "autorita": "Regione Autonoma della Sardegna - Agenzia ADIS"},
        ]

        bacini_map = {}
        for b in bacini_data:
            bac = session.scalar(select(BacinoIdrografico).where(BacinoIdrografico.codice == b["codice"]))
            if not bac:
                bac = BacinoIdrografico(codice=b["codice"], nome=b["nome"], autorita_distretto=b["autorita"])
                session.add(bac)
                session.flush()
            bacini_map[bac.codice] = bac

        print(f"-> Distretti Idrografici censiti: {len(bacini_map)}")

        # 3. Grande Anagrafica Nazionale dei Fiumi Italiani (Coordinate reali WGS84, Fiume, Soglie)
        stazioni_fiumi = [
            # --- PIEMONTE ---
            {"codice": "PIEM_PO_TORINO", "nome": "Po a Torino - Murazzi", "fiume": "Po", "regione": "Piemonte", "bacino": "PO", "lon": 7.6923, "lat": 45.0592, "quota": 215.4, "gialla": 3.5, "arancione": 4.5, "rossa": 5.5, "fonte": "ARPA Piemonte", "scenario": "giallo"},
            {"codice": "PIEM_PO_CARIGNANO", "nome": "Po a Carignano", "fiume": "Po", "regione": "Piemonte", "bacino": "PO", "lon": 7.6745, "lat": 44.9080, "quota": 230.0, "gialla": 4.2, "arancione": 5.4, "rossa": 6.5, "fonte": "ARPA Piemonte", "scenario": "verde"},
            {"codice": "PIEM_TANARO_ALESS", "nome": "Tanaro ad Alessandria", "fiume": "Tanaro", "regione": "Piemonte", "bacino": "PO", "lon": 8.6186, "lat": 44.9133, "quota": 88.2, "gialla": 4.0, "arancione": 5.2, "rossa": 6.5, "fonte": "ARPA Piemonte", "scenario": "verde"},
            {"codice": "PIEM_TANARO_ASTI", "nome": "Tanaro ad Asti", "fiume": "Tanaro", "regione": "Piemonte", "bacino": "PO", "lon": 8.2144, "lat": 44.8912, "quota": 115.0, "gialla": 3.8, "arancione": 4.8, "rossa": 5.8, "fonte": "ARPA Piemonte", "scenario": "verde"},
            {"codice": "PIEM_DORA_RIPARIA", "nome": "Dora Riparia a Susa", "fiume": "Dora Riparia", "regione": "Piemonte", "bacino": "PO", "lon": 7.0505, "lat": 45.1378, "quota": 490.0, "gialla": 2.2, "arancione": 3.2, "rossa": 4.0, "fonte": "ARPA Piemonte", "scenario": "verde"},
            {"codice": "PIEM_SESIA_BORGO", "nome": "Sesia a Borgosesia", "fiume": "Sesia", "regione": "Piemonte", "bacino": "PO", "lon": 8.2778, "lat": 45.7144, "quota": 345.0, "gialla": 3.0, "arancione": 4.2, "rossa": 5.2, "fonte": "ARPA Piemonte", "scenario": "verde"},
            {"codice": "PIEM_STURA_CUNEO", "nome": "Stura di Demonte a Cuneo", "fiume": "Stura di Demonte", "regione": "Piemonte", "bacino": "PO", "lon": 7.5510, "lat": 44.3940, "quota": 520.0, "gialla": 2.5, "arancione": 3.5, "rossa": 4.5, "fonte": "ARPA Piemonte", "scenario": "verde"},
            {"codice": "PIEM_BORMIDA_AL", "nome": "Bormida ad Alessandria", "fiume": "Bormida", "regione": "Piemonte", "bacino": "PO", "lon": 8.6350, "lat": 44.9050, "quota": 85.0, "gialla": 4.5, "arancione": 6.0, "rossa": 7.5, "fonte": "ARPA Piemonte", "scenario": "arancione"},

            # --- VALLE D'AOSTA ---
            {"codice": "VDA_DORA_AOSTA", "nome": "Dora Baltea ad Aosta", "fiume": "Dora Baltea", "regione": "Valle d'Aosta", "bacino": "PO", "lon": 7.3225, "lat": 45.7370, "quota": 560.0, "gialla": 2.0, "arancione": 2.8, "rossa": 3.5, "fonte": "Centro Funzionale VdA", "scenario": "verde"},
            {"codice": "VDA_DORA_DONNAS", "nome": "Dora Baltea a Donnas", "fiume": "Dora Baltea", "regione": "Valle d'Aosta", "bacino": "PO", "lon": 7.7700, "lat": 45.6020, "quota": 310.0, "gialla": 2.8, "arancione": 3.8, "rossa": 4.6, "fonte": "Centro Funzionale VdA", "scenario": "verde"},
            {"codice": "VDA_LYS_PONT", "nome": "Torrente Lys a Pont-Saint-Martin", "fiume": "Lys", "regione": "Valle d'Aosta", "bacino": "PO", "lon": 7.7980, "lat": 45.5980, "quota": 340.0, "gialla": 1.8, "arancione": 2.5, "rossa": 3.2, "fonte": "Centro Funzionale VdA", "scenario": "verde"},

            # --- LOMBARDIA ---
            {"codice": "LOMB_TICINO_PAVIA", "nome": "Ticino a Pavia - Ponte Coperto", "fiume": "Ticino", "regione": "Lombardia", "bacino": "PO", "lon": 9.1534, "lat": 45.1802, "quota": 69.5, "gialla": 2.2, "arancione": 3.0, "rossa": 3.8, "fonte": "ARPA Lombardia", "scenario": "arancione"},
            {"codice": "LOMB_PO_CREMONA", "nome": "Po a Cremona", "fiume": "Po", "regione": "Lombardia", "bacino": "PO", "lon": 10.0215, "lat": 45.1270, "quota": 34.0, "gialla": 3.2, "arancione": 4.2, "rossa": 5.2, "fonte": "AIPO / ARPA Lombardia", "scenario": "verde"},
            {"codice": "LOMB_PO_SANBENEDETTO", "nome": "Po a San Benedetto Po", "fiume": "Po", "regione": "Lombardia", "bacino": "PO", "lon": 10.9320, "lat": 45.0450, "quota": 16.0, "gialla": 3.5, "arancione": 4.8, "rossa": 6.0, "fonte": "AIPO / ARPA Lombardia", "scenario": "verde"},
            {"codice": "LOMB_ADDA_LECCO", "nome": "Adda a Lecco (Uscita Lago di Como)", "fiume": "Adda", "regione": "Lombardia", "bacino": "PO", "lon": 9.3900, "lat": 45.8500, "quota": 198.0, "gialla": 1.5, "arancione": 2.2, "rossa": 2.8, "fonte": "ARPA Lombardia", "scenario": "verde"},
            {"codice": "LOMB_ADDA_CASSANO", "nome": "Adda a Cassano d'Adda", "fiume": "Adda", "regione": "Lombardia", "bacino": "PO", "lon": 9.5160, "lat": 45.5260, "quota": 128.0, "gialla": 2.0, "arancione": 2.8, "rossa": 3.6, "fonte": "ARPA Lombardia", "scenario": "verde"},
            {"codice": "LOMB_ADDA_SPINO", "nome": "Adda a Spino d'Adda", "fiume": "Adda", "regione": "Lombardia", "bacino": "PO", "lon": 9.4950, "lat": 45.4020, "quota": 78.0, "gialla": 2.2, "arancione": 3.1, "rossa": 4.0, "fonte": "ARPA Lombardia", "scenario": "verde"},
            {"codice": "LOMB_OGLIO_PALAZZOLO", "nome": "Oglio a Palazzolo sull'Oglio", "fiume": "Oglio", "regione": "Lombardia", "bacino": "PO", "lon": 9.8820, "lat": 45.5980, "quota": 140.0, "gialla": 1.6, "arancione": 2.3, "rossa": 3.0, "fonte": "ARPA Lombardia", "scenario": "verde"},
            {"codice": "LOMB_OGLIO_MARCARIA", "nome": "Oglio a Marcaria", "fiume": "Oglio", "regione": "Lombardia", "bacino": "PO", "lon": 10.5310, "lat": 45.1220, "quota": 24.0, "gialla": 3.2, "arancione": 4.4, "rossa": 5.4, "fonte": "ARPA Lombardia", "scenario": "verde"},
            {"codice": "LOMB_MINCIO_MANTOVA", "nome": "Mincio a Mantova (Lago Inferiore)", "fiume": "Mincio", "regione": "Lombardia", "bacino": "PO", "lon": 10.8030, "lat": 45.1610, "quota": 17.5, "gialla": 1.4, "arancione": 1.9, "rossa": 2.5, "fonte": "ARPA Lombardia", "scenario": "verde"},
            {"codice": "LOMB_BREMBO_PONTE", "nome": "Brembo a Ponte San Pietro", "fiume": "Brembo", "regione": "Lombardia", "bacino": "PO", "lon": 9.5850, "lat": 45.6980, "quota": 218.0, "gialla": 1.8, "arancione": 2.6, "rossa": 3.4, "fonte": "ARPA Lombardia", "scenario": "verde"},
            {"codice": "LOMB_SERIO_ALZANO", "nome": "Serio ad Alzano Lombardo", "fiume": "Serio", "regione": "Lombardia", "bacino": "PO", "lon": 9.7310, "lat": 45.7310, "quota": 290.0, "gialla": 1.7, "arancione": 2.5, "rossa": 3.2, "fonte": "ARPA Lombardia", "scenario": "verde"},
            {"codice": "LOMB_LAMBRO_MILANO", "nome": "Lambro a Milano Parco Lambro", "fiume": "Lambro", "regione": "Lombardia", "bacino": "PO", "lon": 9.2450, "lat": 45.4950, "quota": 118.0, "gialla": 1.9, "arancione": 2.6, "rossa": 3.2, "fonte": "ARPA Lombardia", "scenario": "giallo"},
            {"codice": "LOMB_OLONA_LEGNANO", "nome": "Olona a Legnano", "fiume": "Olona", "regione": "Lombardia", "bacino": "PO", "lon": 8.9160, "lat": 45.5960, "quota": 195.0, "gialla": 1.6, "arancione": 2.2, "rossa": 2.8, "fonte": "ARPA Lombardia", "scenario": "verde"},

            # --- TRENTINO-ALTO ADIGE ---
            {"codice": "TAA_ADIGE_BOLZANO", "nome": "Adige a Bolzano - Ponte Roma", "fiume": "Adige", "regione": "Trentino-Alto Adige", "bacino": "ALPI_ORIENTALI", "lon": 11.3410, "lat": 46.4880, "quota": 250.0, "gialla": 3.0, "arancione": 4.0, "rossa": 5.0, "fonte": "Provincia Autonoma Bolzano", "scenario": "verde"},
            {"codice": "TAA_ADIGE_TRENTO", "nome": "Adige a Trento - Ponte San Lorenzo", "fiume": "Adige", "regione": "Trentino-Alto Adige", "bacino": "ALPI_ORIENTALI", "lon": 11.1180, "lat": 46.0710, "quota": 190.0, "gialla": 3.5, "arancione": 4.5, "rossa": 5.5, "fonte": "Provincia Autonoma Trento", "scenario": "verde"},
            {"codice": "TAA_ISARCO_BRESS", "nome": "Isarco a Bressanone", "fiume": "Isarco", "regione": "Trentino-Alto Adige", "bacino": "ALPI_ORIENTALI", "lon": 11.6570, "lat": 46.7160, "quota": 555.0, "gialla": 2.2, "arancione": 3.0, "rossa": 3.8, "fonte": "Provincia Autonoma Bolzano", "scenario": "verde"},
            {"codice": "TAA_NOCE_MEZZOLOM", "nome": "Noce a Mezzolombardo", "fiume": "Noce", "regione": "Trentino-Alto Adige", "bacino": "ALPI_ORIENTALI", "lon": 11.0960, "lat": 46.2140, "quota": 215.0, "gialla": 2.0, "arancione": 2.8, "rossa": 3.6, "fonte": "Provincia Autonoma Trento", "scenario": "verde"},
            {"codice": "TAA_AVISIO_LAVIS", "nome": "Avisio a Lavis", "fiume": "Avisio", "regione": "Trentino-Alto Adige", "bacino": "ALPI_ORIENTALI", "lon": 11.1100, "lat": 46.1390, "quota": 230.0, "gialla": 2.5, "arancione": 3.5, "rossa": 4.3, "fonte": "Provincia Autonoma Trento", "scenario": "verde"},

            # --- VENETO ---
            {"codice": "VEN_ADIGE_VERONA", "nome": "Adige a Verona - Ponte Nuovo", "fiume": "Adige", "regione": "Veneto", "bacino": "ALPI_ORIENTALI", "lon": 11.0006, "lat": 45.4431, "quota": 45.1, "gialla": 1.8, "arancione": 2.8, "rossa": 3.8, "fonte": "ARPAV Veneto", "scenario": "verde"},
            {"codice": "VEN_ADIGE_LEGNAGO", "nome": "Adige a Legnago", "fiume": "Adige", "regione": "Veneto", "bacino": "ALPI_ORIENTALI", "lon": 11.3110, "lat": 45.1930, "quota": 14.0, "gialla": 2.5, "arancione": 3.8, "rossa": 5.0, "fonte": "ARPAV Veneto", "scenario": "verde"},
            {"codice": "VEN_ADIGE_BOARA", "nome": "Adige a Boara Pisani", "fiume": "Adige", "regione": "Veneto", "bacino": "ALPI_ORIENTALI", "lon": 11.7820, "lat": 45.1050, "quota": 6.5, "gialla": 3.0, "arancione": 4.2, "rossa": 5.5, "fonte": "ARPAV Veneto", "scenario": "verde"},
            {"codice": "VEN_BACCHIGLIONE_VIC", "nome": "Bacchiglione a Vicenza - Ponte Angeli", "fiume": "Bacchiglione", "regione": "Veneto", "bacino": "ALPI_ORIENTALI", "lon": 11.5490, "lat": 45.5480, "quota": 38.0, "gialla": 4.5, "arancione": 5.5, "rossa": 6.3, "fonte": "ARPAV Veneto", "scenario": "giallo"},
            {"codice": "VEN_BRENTA_BASSANO", "nome": "Brenta a Bassano del Grappa", "fiume": "Brenta", "regione": "Veneto", "bacino": "ALPI_ORIENTALI", "lon": 11.7330, "lat": 45.7660, "quota": 125.0, "gialla": 2.0, "arancione": 2.9, "rossa": 3.8, "fonte": "ARPAV Veneto", "scenario": "verde"},
            {"codice": "VEN_BRENTA_LIMENA", "nome": "Brenta a Limena", "fiume": "Brenta", "regione": "Veneto", "bacino": "ALPI_ORIENTALI", "lon": 11.8480, "lat": 45.4740, "quota": 21.0, "gialla": 3.2, "arancione": 4.3, "rossa": 5.2, "fonte": "ARPAV Veneto", "scenario": "verde"},
            {"codice": "VEN_PIAVE_NERVESA", "nome": "Piave a Nervesa della Battaglia", "fiume": "Piave", "regione": "Veneto", "bacino": "ALPI_ORIENTALI", "lon": 12.2150, "lat": 45.8240, "quota": 72.0, "gialla": 2.5, "arancione": 3.5, "rossa": 4.5, "fonte": "ARPAV Veneto", "scenario": "verde"},
            {"codice": "VEN_PIAVE_SANDONA", "nome": "Piave a San Donà di Piave", "fiume": "Piave", "regione": "Veneto", "bacino": "ALPI_ORIENTALI", "lon": 12.5650, "lat": 45.6320, "quota": 4.0, "gialla": 3.2, "arancione": 4.4, "rossa": 5.5, "fonte": "ARPAV Veneto", "scenario": "verde"},
            {"codice": "VEN_SILE_TREVISO", "nome": "Sile a Treviso", "fiume": "Sile", "regione": "Veneto", "bacino": "ALPI_ORIENTALI", "lon": 12.2470, "lat": 45.6630, "quota": 14.0, "gialla": 1.4, "arancione": 1.9, "rossa": 2.5, "fonte": "ARPAV Veneto", "scenario": "verde"},
            {"codice": "VEN_LIVENZA_MOTTA", "nome": "Livenza a Motta di Livenza", "fiume": "Livenza", "regione": "Veneto", "bacino": "ALPI_ORIENTALI", "lon": 12.6100, "lat": 45.7720, "quota": 6.0, "gialla": 5.5, "arancione": 7.0, "rossa": 8.2, "fonte": "ARPAV Veneto", "scenario": "arancione"},

            # --- FRIULI-VENEZIA GIULIA ---
            {"codice": "FVG_TAGLIAMENTO_VENZ", "nome": "Tagliamento a Venzone", "fiume": "Tagliamento", "regione": "Friuli-Venezia Giulia", "bacino": "ALPI_ORIENTALI", "lon": 13.1360, "lat": 46.3310, "quota": 225.0, "gialla": 2.2, "arancione": 3.2, "rossa": 4.2, "fonte": "ARPA FVG", "scenario": "verde"},
            {"codice": "FVG_TAGLIAMENTO_PINZ", "nome": "Tagliamento a Pinzano al Tagliamento", "fiume": "Tagliamento", "regione": "Friuli-Venezia Giulia", "bacino": "ALPI_ORIENTALI", "lon": 12.9460, "lat": 46.1820, "quota": 145.0, "gialla": 3.0, "arancione": 4.5, "rossa": 5.8, "fonte": "ARPA FVG", "scenario": "verde"},
            {"codice": "FVG_TAGLIAMENTO_LATIS", "nome": "Tagliamento a Latisana", "fiume": "Tagliamento", "regione": "Friuli-Venezia Giulia", "bacino": "ALPI_ORIENTALI", "lon": 13.0030, "lat": 45.7770, "quota": 7.0, "gialla": 6.0, "arancione": 7.5, "rossa": 8.7, "fonte": "ARPA FVG", "scenario": "giallo"},
            {"codice": "FVG_ISONZO_GORIZIA", "nome": "Isonzo a Gorizia", "fiume": "Isonzo", "regione": "Friuli-Venezia Giulia", "bacino": "ALPI_ORIENTALI", "lon": 13.6210, "lat": 45.9430, "quota": 72.0, "gialla": 2.5, "arancione": 3.8, "rossa": 5.0, "fonte": "ARPA FVG", "scenario": "verde"},
            {"codice": "FVG_NATISONE_CIVID", "nome": "Natisone a Cividale del Friuli", "fiume": "Natisone", "regione": "Friuli-Venezia Giulia", "bacino": "ALPI_ORIENTALI", "lon": 13.4320, "lat": 46.0920, "quota": 132.0, "gialla": 2.0, "arancione": 3.0, "rossa": 4.0, "fonte": "ARPA FVG", "scenario": "verde"},

            # --- LIGURIA ---
            {"codice": "LIG_MAGRA_SANTOSTEF", "nome": "Magra a Santo Stefano di Magra", "fiume": "Magra", "regione": "Liguria", "bacino": "APPENNINO_SETT", "lon": 9.9140, "lat": 44.1560, "quota": 25.0, "gialla": 2.0, "arancione": 3.0, "rossa": 4.0, "fonte": "ARPAL Liguria", "scenario": "verde"},
            {"codice": "LIG_VARA_BRUGNATO", "nome": "Vara a Brugnato", "fiume": "Vara", "regione": "Liguria", "bacino": "APPENNINO_SETT", "lon": 9.7210, "lat": 44.2360, "quota": 105.0, "gialla": 2.5, "arancione": 3.5, "rossa": 4.8, "fonte": "ARPAL Liguria", "scenario": "verde"},
            {"codice": "LIG_ENTELLA_CHIAVARI", "nome": "Entella a Chiavari", "fiume": "Entella", "regione": "Liguria", "bacino": "APPENNINO_SETT", "lon": 9.3240, "lat": 44.3160, "quota": 5.0, "gialla": 2.0, "arancione": 2.9, "rossa": 3.8, "fonte": "ARPAL Liguria", "scenario": "verde"},
            {"codice": "LIG_BISAGNO_GENOVA", "nome": "Bisagno a Genova - Borgo Incrociati", "fiume": "Bisagno", "regione": "Liguria", "bacino": "APPENNINO_SETT", "lon": 8.9480, "lat": 44.4110, "quota": 12.0, "gialla": 1.5, "arancione": 2.3, "rossa": 3.0, "fonte": "ARPAL Liguria", "scenario": "giallo"},
            {"codice": "LIG_POLCEVERA_RIVAR", "nome": "Polcevera a Genova Rivarolo", "fiume": "Polcevera", "regione": "Liguria", "bacino": "APPENNINO_SETT", "lon": 8.8920, "lat": 44.4370, "quota": 25.0, "gialla": 1.4, "arancione": 2.1, "rossa": 2.8, "fonte": "ARPAL Liguria", "scenario": "verde"},
            {"codice": "LIG_CENTA_ALBENGA", "nome": "Centa ad Albenga", "fiume": "Centa", "regione": "Liguria", "bacino": "APPENNINO_SETT", "lon": 8.2140, "lat": 44.0510, "quota": 8.0, "gialla": 2.2, "arancione": 3.2, "rossa": 4.2, "fonte": "ARPAL Liguria", "scenario": "verde"},
            {"codice": "LIG_ROIA_VENTIMIGLIA", "nome": "Roia a Ventimiglia", "fiume": "Roia", "regione": "Liguria", "bacino": "APPENNINO_SETT", "lon": 7.6040, "lat": 43.7910, "quota": 6.0, "gialla": 2.0, "arancione": 3.0, "rossa": 4.0, "fonte": "ARPAL Liguria", "scenario": "verde"},

            # --- EMILIA-ROMAGNA ---
            {"codice": "EMIL_PO_PIACENZA", "nome": "Po a Piacenza", "fiume": "Po", "regione": "Emilia-Romagna", "bacino": "PO", "lon": 9.6974, "lat": 45.0601, "quota": 48.0, "gialla": 5.0, "arancione": 6.5, "rossa": 8.0, "fonte": "ARPAE Emilia-Romagna", "scenario": "verde"},
            {"codice": "EMIL_PO_BORETTO", "nome": "Po a Boretto", "fiume": "Po", "regione": "Emilia-Romagna", "bacino": "PO", "lon": 10.5510, "lat": 44.9080, "quota": 21.0, "gialla": 4.5, "arancione": 5.8, "rossa": 7.2, "fonte": "ARPAE Emilia-Romagna", "scenario": "verde"},
            {"codice": "EMIL_PO_PONTELAGO", "nome": "Po a Pontelagoscuro (Ferrara)", "fiume": "Po", "regione": "Emilia-Romagna", "bacino": "PO", "lon": 11.6062, "lat": 44.8837, "quota": 8.5, "gialla": 1.5, "arancione": 2.5, "rossa": 3.5, "fonte": "ARPAE Emilia-Romagna", "scenario": "rosso"},
            {"codice": "EMIL_TREBBIA_RIVERG", "nome": "Trebbia a Rivergaro", "fiume": "Trebbia", "regione": "Emilia-Romagna", "bacino": "PO", "lon": 9.6010, "lat": 44.9560, "quota": 138.0, "gialla": 2.2, "arancione": 3.2, "rossa": 4.5, "fonte": "ARPAE Emilia-Romagna", "scenario": "verde"},
            {"codice": "EMIL_TARO_FORNOVO", "nome": "Taro a Fornovo di Taro", "fiume": "Taro", "regione": "Emilia-Romagna", "bacino": "PO", "lon": 10.1010, "lat": 44.6910, "quota": 150.0, "gialla": 1.8, "arancione": 2.7, "rossa": 3.8, "fonte": "ARPAE Emilia-Romagna", "scenario": "verde"},
            {"codice": "EMIL_ENZA_SORBOLO", "nome": "Enza a Sorbolo", "fiume": "Enza", "regione": "Emilia-Romagna", "bacino": "PO", "lon": 10.4500, "lat": 44.8510, "quota": 34.0, "gialla": 9.0, "arancione": 10.5, "rossa": 11.8, "fonte": "ARPAE Emilia-Romagna", "scenario": "arancione"},
            {"codice": "EMIL_SECCHIA_RUBIERA", "nome": "Secchia a Rubiera", "fiume": "Secchia", "regione": "Emilia-Romagna", "bacino": "PO", "lon": 10.7780, "lat": 44.6540, "quota": 54.0, "gialla": 1.8, "arancione": 2.6, "rossa": 3.5, "fonte": "ARPAE Emilia-Romagna", "scenario": "verde"},
            {"codice": "EMIL_SECCHIA_PONTEALTO", "nome": "Secchia a Ponte Alto (Modena)", "fiume": "Secchia", "regione": "Emilia-Romagna", "bacino": "PO", "lon": 10.9020, "lat": 44.6730, "quota": 32.0, "gialla": 8.0, "arancione": 9.5, "rossa": 10.8, "fonte": "ARPAE Emilia-Romagna", "scenario": "rosso"},
            {"codice": "EMIL_PANARO_SANTAMBR", "nome": "Panaro a Ponte Sant'Ambrogio", "fiume": "Panaro", "regione": "Emilia-Romagna", "bacino": "PO", "lon": 10.9780, "lat": 44.6180, "quota": 36.0, "gialla": 8.5, "arancione": 10.0, "rossa": 11.5, "fonte": "ARPAE Emilia-Romagna", "scenario": "verde"},
            {"codice": "EMIL_RENO_CASALECCHIO", "nome": "Reno a Casalecchio di Reno", "fiume": "Reno", "regione": "Emilia-Romagna", "bacino": "PO", "lon": 11.2781, "lat": 44.4789, "quota": 61.0, "gialla": 1.6, "arancione": 2.2, "rossa": 2.8, "fonte": "ARPAE Emilia-Romagna", "scenario": "verde"},
            {"codice": "EMIL_SANTERNO_IMOLA", "nome": "Santerno ad Imola", "fiume": "Santerno", "regione": "Emilia-Romagna", "bacino": "PO", "lon": 11.7160, "lat": 44.3540, "quota": 47.0, "gialla": 1.8, "arancione": 2.5, "rossa": 3.2, "fonte": "ARPAE Emilia-Romagna", "scenario": "verde"},
            {"codice": "EMIL_LAMONE_FAENZA", "nome": "Lamone a Faenza", "fiume": "Lamone", "regione": "Emilia-Romagna", "bacino": "PO", "lon": 11.8790, "lat": 44.2880, "quota": 35.0, "gialla": 4.0, "arancione": 5.2, "rossa": 6.2, "fonte": "ARPAE Emilia-Romagna", "scenario": "arancione"},
            {"codice": "EMIL_SAVIO_CESENA", "nome": "Savio a Cesena", "fiume": "Savio", "regione": "Emilia-Romagna", "bacino": "PO", "lon": 12.2380, "lat": 44.1390, "quota": 44.0, "gialla": 5.0, "arancione": 6.5, "rossa": 7.5, "fonte": "ARPAE Emilia-Romagna", "scenario": "verde"},
            {"codice": "EMIL_MARECCHIA_RIMINI", "nome": "Marecchia a Rimini", "fiume": "Marecchia", "regione": "Emilia-Romagna", "bacino": "PO", "lon": 12.5610, "lat": 44.0620, "quota": 4.0, "gialla": 2.0, "arancione": 3.0, "rossa": 4.0, "fonte": "ARPAE Emilia-Romagna", "scenario": "verde"},

            # --- TOSCANA ---
            {"codice": "TOSC_ARNO_FIRENZE", "nome": "Arno a Firenze - Uffizi", "fiume": "Arno", "regione": "Toscana", "bacino": "APPENNINO_SETT", "lon": 11.2558, "lat": 43.7674, "quota": 42.0, "gialla": 3.0, "arancione": 4.5, "rossa": 5.5, "fonte": "CFR Toscana", "scenario": "giallo"},
            {"codice": "TOSC_ARNO_PISA", "nome": "Arno a Pisa - Sostegno", "fiume": "Arno", "regione": "Toscana", "bacino": "APPENNINO_SETT", "lon": 10.4010, "lat": 43.7160, "quota": 3.0, "gialla": 3.5, "arancione": 4.5, "rossa": 5.5, "fonte": "CFR Toscana", "scenario": "verde"},
            {"codice": "TOSC_ARNO_PONTASS", "nome": "Arno a Pontassieve", "fiume": "Arno", "regione": "Toscana", "bacino": "APPENNINO_SETT", "lon": 11.4320, "lat": 43.7740, "quota": 90.0, "gialla": 4.0, "arancione": 5.5, "rossa": 7.0, "fonte": "CFR Toscana", "scenario": "verde"},
            {"codice": "TOSC_SIEVE_SANPIERO", "nome": "Sieve a San Piero a Sieve", "fiume": "Sieve", "regione": "Toscana", "bacino": "APPENNINO_SETT", "lon": 11.3250, "lat": 43.9590, "quota": 210.0, "gialla": 2.5, "arancione": 3.5, "rossa": 4.5, "fonte": "CFR Toscana", "scenario": "verde"},
            {"codice": "TOSC_BISENZIO_PRATO", "nome": "Bisenzio a Prato - Cavalciotto", "fiume": "Bisenzio", "regione": "Toscana", "bacino": "APPENNINO_SETT", "lon": 11.0960, "lat": 43.8820, "quota": 65.0, "gialla": 2.0, "arancione": 3.0, "rossa": 4.0, "fonte": "CFR Toscana", "scenario": "arancione"},
            {"codice": "TOSC_SERCHIO_LUCCA", "nome": "Serchio a Lucca - Monte San Quirico", "fiume": "Serchio", "regione": "Toscana", "bacino": "APPENNINO_SETT", "lon": 10.5050, "lat": 43.8560, "quota": 20.0, "gialla": 6.5, "arancione": 8.0, "rossa": 9.5, "fonte": "CFR Toscana", "scenario": "verde"},
            {"codice": "TOSC_OMBRONE_GR", "nome": "Ombrone Grossetano a Grosseto", "fiume": "Ombrone", "regione": "Toscana", "bacino": "APPENNINO_SETT", "lon": 11.1120, "lat": 42.7630, "quota": 10.0, "gialla": 4.0, "arancione": 5.5, "rossa": 6.8, "fonte": "CFR Toscana", "scenario": "verde"},
            {"codice": "TOSC_CECINA_CECINA", "nome": "Cecina a Cecina", "fiume": "Cecina", "regione": "Toscana", "bacino": "APPENNINO_SETT", "lon": 10.5210, "lat": 43.3150, "quota": 15.0, "gialla": 2.5, "arancione": 3.8, "rossa": 5.0, "fonte": "CFR Toscana", "scenario": "verde"},

            # --- UMBRIA ---
            {"codice": "UMB_TEVERE_CITTACAST", "nome": "Tevere a Città di Castello", "fiume": "Tevere", "regione": "Umbria", "bacino": "APPENNINO_CENT", "lon": 12.2410, "lat": 43.4570, "quota": 288.0, "gialla": 3.0, "arancione": 4.5, "rossa": 5.8, "fonte": "Centro Funzionale Umbria", "scenario": "verde"},
            {"codice": "UMB_TEVERE_TORGIANO", "nome": "Tevere a Ponte Nuovo (Torgiano)", "fiume": "Tevere", "regione": "Umbria", "bacino": "APPENNINO_CENT", "lon": 12.4340, "lat": 43.0240, "quota": 195.0, "gialla": 4.0, "arancione": 5.5, "rossa": 7.0, "fonte": "Centro Funzionale Umbria", "scenario": "verde"},
            {"codice": "UMB_CHIASCIO_PETRIG", "nome": "Chiascio a Petrignano d'Assisi", "fiume": "Chiascio", "regione": "Umbria", "bacino": "APPENNINO_CENT", "lon": 12.5280, "lat": 43.1090, "quota": 210.0, "gialla": 2.5, "arancione": 3.8, "rossa": 5.0, "fonte": "Centro Funzionale Umbria", "scenario": "verde"},
            {"codice": "UMB_NERA_TERNI", "nome": "Nera a Terni", "fiume": "Nera", "regione": "Umbria", "bacino": "APPENNINO_CENT", "lon": 12.6450, "lat": 42.5630, "quota": 125.0, "gialla": 2.2, "arancione": 3.2, "rossa": 4.2, "fonte": "Centro Funzionale Umbria", "scenario": "verde"},
            {"codice": "UMB_PAGLIA_ORVIETO", "nome": "Paglia ad Orvieto Scalo", "fiume": "Paglia", "regione": "Umbria", "bacino": "APPENNINO_CENT", "lon": 12.1320, "lat": 42.7210, "quota": 110.0, "gialla": 3.5, "arancione": 5.0, "rossa": 6.5, "fonte": "Centro Funzionale Umbria", "scenario": "giallo"},

            # --- MARCHE ---
            {"codice": "MAR_METAURO_FANO", "nome": "Metauro a Fano", "fiume": "Metauro", "regione": "Marche", "bacino": "APPENNINO_CENT", "lon": 13.0180, "lat": 43.8390, "quota": 12.0, "gialla": 2.5, "arancione": 3.5, "rossa": 4.5, "fonte": "Protezione Civile Marche", "scenario": "verde"},
            {"codice": "MAR_FOGLIA_PESARO", "nome": "Foglia a Pesaro", "fiume": "Foglia", "regione": "Marche", "bacino": "APPENNINO_CENT", "lon": 12.9090, "lat": 43.9110, "quota": 8.0, "gialla": 2.2, "arancione": 3.0, "rossa": 4.0, "fonte": "Protezione Civile Marche", "scenario": "verde"},
            {"codice": "MAR_ESINO_JESI", "nome": "Esino a Jesi", "fiume": "Esino", "regione": "Marche", "bacino": "APPENNINO_CENT", "lon": 13.2450, "lat": 43.5220, "quota": 65.0, "gialla": 2.5, "arancione": 3.8, "rossa": 4.8, "fonte": "Protezione Civile Marche", "scenario": "verde"},
            {"codice": "MAR_POTENZA_MACERATA", "nome": "Potenza a Villa Potenza (Macerata)", "fiume": "Potenza", "regione": "Marche", "bacino": "APPENNINO_CENT", "lon": 13.4510, "lat": 43.3010, "quota": 85.0, "gialla": 2.0, "arancione": 3.0, "rossa": 4.2, "fonte": "Protezione Civile Marche", "scenario": "verde"},
            {"codice": "MAR_CHIENTI_CIVITAN", "nome": "Chienti a Civitanova Marche", "fiume": "Chienti", "regione": "Marche", "bacino": "APPENNINO_CENT", "lon": 13.7250, "lat": 43.3090, "quota": 6.0, "gialla": 2.2, "arancione": 3.2, "rossa": 4.4, "fonte": "Protezione Civile Marche", "scenario": "verde"},
            {"codice": "MAR_TRONTO_ASCOLI", "nome": "Tronto ad Ascoli Piceno", "fiume": "Tronto", "regione": "Marche", "bacino": "APPENNINO_CENT", "lon": 13.5750, "lat": 42.8550, "quota": 150.0, "gialla": 2.5, "arancione": 3.5, "rossa": 4.5, "fonte": "Protezione Civile Marche", "scenario": "verde"},

            # --- LAZIO ---
            {"codice": "LAZ_TEVERE_RIPETTA", "nome": "Tevere a Roma - Ripetta", "fiume": "Tevere", "regione": "Lazio", "bacino": "APPENNINO_CENT", "lon": 12.4741, "lat": 41.9056, "quota": 5.2, "gialla": 7.0, "arancione": 9.5, "rossa": 12.0, "fonte": "Protezione Civile Lazio", "scenario": "verde"},
            {"codice": "LAZ_TEVERE_FIUMICINO", "nome": "Tevere a Fiumicino (Foce)", "fiume": "Tevere", "regione": "Lazio", "bacino": "APPENNINO_CENT", "lon": 12.2510, "lat": 41.7720, "quota": 1.5, "gialla": 2.0, "arancione": 2.8, "rossa": 3.5, "fonte": "Protezione Civile Lazio", "scenario": "verde"},
            {"codice": "LAZ_ANIENE_MAMMOLO", "nome": "Aniene a Roma - Ponte Mammolo", "fiume": "Aniene", "regione": "Lazio", "bacino": "APPENNINO_CENT", "lon": 12.5680, "lat": 41.9210, "quota": 22.0, "gialla": 3.5, "arancione": 5.0, "rossa": 6.5, "fonte": "Protezione Civile Lazio", "scenario": "verde"},
            {"codice": "LAZ_ANIENE_TIVOLI", "nome": "Aniene a Tivoli", "fiume": "Aniene", "regione": "Lazio", "bacino": "APPENNINO_CENT", "lon": 12.7980, "lat": 41.9610, "quota": 220.0, "gialla": 2.2, "arancione": 3.2, "rossa": 4.2, "fonte": "Protezione Civile Lazio", "scenario": "verde"},
            {"codice": "LAZ_SACCO_CECCANO", "nome": "Sacco a Ceccano", "fiume": "Sacco", "regione": "Lazio", "bacino": "APPENNINO_MERID", "lon": 13.3320, "lat": 41.5670, "quota": 95.0, "gialla": 3.5, "arancione": 5.0, "rossa": 6.2, "fonte": "Protezione Civile Lazio", "scenario": "giallo"},
            {"codice": "LAZ_LIRI_SORA", "nome": "Liri a Sora", "fiume": "Liri", "regione": "Lazio", "bacino": "APPENNINO_MERID", "lon": 13.6120, "lat": 41.7160, "quota": 280.0, "gialla": 2.5, "arancione": 3.6, "rossa": 4.8, "fonte": "Protezione Civile Lazio", "scenario": "verde"},
            {"codice": "LAZ_GARIGLIANO_MINTURNO", "nome": "Garigliano a Minturno", "fiume": "Garigliano", "regione": "Lazio", "bacino": "APPENNINO_MERID", "lon": 13.7550, "lat": 41.2580, "quota": 4.0, "gialla": 4.5, "arancione": 6.0, "rossa": 7.5, "fonte": "Protezione Civile Lazio", "scenario": "verde"},
            {"codice": "LAZ_MARTA_TARQUINIA", "nome": "Marta a Tarquinia", "fiume": "Marta", "regione": "Lazio", "bacino": "APPENNINO_CENT", "lon": 11.7580, "lat": 42.2490, "quota": 25.0, "gialla": 2.0, "arancione": 2.8, "rossa": 3.6, "fonte": "Protezione Civile Lazio", "scenario": "verde"},

            # --- ABRUZZO ---
            {"codice": "ABR_ATERNO_LAQUILA", "nome": "Aterno a L'Aquila", "fiume": "Aterno", "regione": "Abruzzo", "bacino": "APPENNINO_CENT", "lon": 13.3980, "lat": 42.3510, "quota": 680.0, "gialla": 1.8, "arancione": 2.6, "rossa": 3.5, "fonte": "Centro Funzionale Abruzzo", "scenario": "verde"},
            {"codice": "ABR_PESCARA_PESCARA", "nome": "Pescara a Pescara (Foce)", "fiume": "Pescara", "regione": "Abruzzo", "bacino": "APPENNINO_CENT", "lon": 14.2140, "lat": 42.4640, "quota": 2.0, "gialla": 3.0, "arancione": 4.2, "rossa": 5.5, "fonte": "Centro Funzionale Abruzzo", "scenario": "verde"},
            {"codice": "ABR_SANGRO_CASTEL", "nome": "Sangro a Castel di Sangro", "fiume": "Sangro", "regione": "Abruzzo", "bacino": "APPENNINO_MERID", "lon": 14.1080, "lat": 41.7820, "quota": 790.0, "gialla": 2.0, "arancione": 2.9, "rossa": 3.8, "fonte": "Centro Funzionale Abruzzo", "scenario": "verde"},
            {"codice": "ABR_VOMANO_ROSETO", "nome": "Vomano a Roseto degli Abruzzi", "fiume": "Vomano", "regione": "Abruzzo", "bacino": "APPENNINO_CENT", "lon": 14.0150, "lat": 42.6730, "quota": 8.0, "gialla": 2.5, "arancione": 3.8, "rossa": 5.0, "fonte": "Centro Funzionale Abruzzo", "scenario": "verde"},
            {"codice": "ABR_TORDINO_GIULIAN", "nome": "Tordino a Giulianova", "fiume": "Tordino", "regione": "Abruzzo", "bacino": "APPENNINO_CENT", "lon": 13.9620, "lat": 42.7510, "quota": 6.0, "gialla": 2.2, "arancione": 3.2, "rossa": 4.2, "fonte": "Centro Funzionale Abruzzo", "scenario": "verde"},

            # --- MOLISE ---
            {"codice": "MOL_BIFERNO_BOJANO", "nome": "Biferno a Bojano", "fiume": "Biferno", "regione": "Molise", "bacino": "APPENNINO_MERID", "lon": 14.4750, "lat": 41.4850, "quota": 480.0, "gialla": 1.6, "arancione": 2.4, "rossa": 3.2, "fonte": "Protezione Civile Molise", "scenario": "verde"},
            {"codice": "MOL_BIFERNO_TERMOLI", "nome": "Biferno a Termoli (Foce)", "fiume": "Biferno", "regione": "Molise", "bacino": "APPENNINO_MERID", "lon": 14.9960, "lat": 41.9980, "quota": 3.0, "gialla": 3.0, "arancione": 4.5, "rossa": 5.8, "fonte": "Protezione Civile Molise", "scenario": "giallo"},
            {"codice": "MOL_VOLTURNO_COLLI", "nome": "Volturno a Colli a Volturno", "fiume": "Volturno", "regione": "Molise", "bacino": "APPENNINO_MERID", "lon": 14.1020, "lat": 41.5980, "quota": 390.0, "gialla": 2.0, "arancione": 2.8, "rossa": 3.8, "fonte": "Protezione Civile Molise", "scenario": "verde"},
            {"codice": "MOL_TRIGNO_MONTENERO", "nome": "Trigno a Montenero di Bisaccia", "fiume": "Trigno", "regione": "Molise", "bacino": "APPENNINO_MERID", "lon": 14.7820, "lat": 42.0510, "quota": 15.0, "gialla": 2.5, "arancione": 3.6, "rossa": 4.8, "fonte": "Protezione Civile Molise", "scenario": "verde"},

            # --- CAMPANIA ---
            {"codice": "CAM_VOLTURNO_CAPUA", "nome": "Volturno a Capua", "fiume": "Volturno", "regione": "Campania", "bacino": "APPENNINO_MERID", "lon": 14.2120, "lat": 41.1070, "quota": 22.0, "gialla": 5.0, "arancione": 6.5, "rossa": 8.0, "fonte": "Protezione Civile Campania", "scenario": "arancione"},
            {"codice": "CAM_VOLTURNO_AMOROSI", "nome": "Volturno ad Amorosi", "fiume": "Volturno", "regione": "Campania", "bacino": "APPENNINO_MERID", "lon": 14.4630, "lat": 41.2050, "quota": 48.0, "gialla": 4.2, "arancione": 5.6, "rossa": 7.0, "fonte": "Protezione Civile Campania", "scenario": "verde"},
            {"codice": "CAM_CALORE_BENEVENTO", "nome": "Calore Irpino a Benevento", "fiume": "Calore Irpino", "regione": "Campania", "bacino": "APPENNINO_MERID", "lon": 14.7780, "lat": 41.1310, "quota": 130.0, "gialla": 3.5, "arancione": 5.0, "rossa": 6.5, "fonte": "Protezione Civile Campania", "scenario": "rosso"},
            {"codice": "CAM_SELE_EBOLI", "nome": "Sele ad Eboli", "fiume": "Sele", "regione": "Campania", "bacino": "APPENNINO_MERID", "lon": 15.0560, "lat": 40.5420, "quota": 35.0, "gialla": 3.2, "arancione": 4.5, "rossa": 5.8, "fonte": "Protezione Civile Campania", "scenario": "verde"},
            {"codice": "CAM_TANAGRO_POLLA", "nome": "Tanagro a Polla", "fiume": "Tanagro", "regione": "Campania", "bacino": "APPENNINO_MERID", "lon": 15.5180, "lat": 40.5180, "quota": 460.0, "gialla": 2.5, "arancione": 3.8, "rossa": 4.8, "fonte": "Protezione Civile Campania", "scenario": "verde"},
            {"codice": "CAM_SARNO_STABIA", "nome": "Sarno a Castellammare di Stabia", "fiume": "Sarno", "regione": "Campania", "bacino": "APPENNINO_MERID", "lon": 14.4820, "lat": 40.7180, "quota": 4.0, "gialla": 1.8, "arancione": 2.5, "rossa": 3.2, "fonte": "Protezione Civile Campania", "scenario": "verde"},

            # --- PUGLIA ---
            {"codice": "PUG_OFANTO_CERIGNOLA", "nome": "Ofanto a Cerignola", "fiume": "Ofanto", "regione": "Puglia", "bacino": "APPENNINO_MERID", "lon": 15.9020, "lat": 41.2610, "quota": 55.0, "gialla": 3.0, "arancione": 4.5, "rossa": 6.0, "fonte": "Protezione Civile Puglia", "scenario": "verde"},
            {"codice": "PUG_OFANTO_BARLETTA", "nome": "Ofanto a Barletta (Foce)", "fiume": "Ofanto", "regione": "Puglia", "bacino": "APPENNINO_MERID", "lon": 16.2780, "lat": 41.3210, "quota": 5.0, "gialla": 3.5, "arancione": 5.0, "rossa": 6.5, "fonte": "Protezione Civile Puglia", "scenario": "verde"},
            {"codice": "PUG_CANDELARO_MANFRED", "nome": "Candelaro a Manfredonia", "fiume": "Candelaro", "regione": "Puglia", "bacino": "APPENNINO_MERID", "lon": 15.9120, "lat": 41.6250, "quota": 8.0, "gialla": 2.5, "arancione": 3.8, "rossa": 5.0, "fonte": "Protezione Civile Puglia", "scenario": "verde"},
            {"codice": "PUG_CERVARO_FOGGIA", "nome": "Cervaro a Foggia - Incoronata", "fiume": "Cervaro", "regione": "Puglia", "bacino": "APPENNINO_MERID", "lon": 15.5520, "lat": 41.4610, "quota": 45.0, "gialla": 2.2, "arancione": 3.2, "rossa": 4.5, "fonte": "Protezione Civile Puglia", "scenario": "giallo"},

            # --- BASILICATA ---
            {"codice": "BAS_BASENTO_POTENZA", "nome": "Basento a Potenza", "fiume": "Basento", "regione": "Basilicata", "bacino": "APPENNINO_MERID", "lon": 15.8050, "lat": 40.6410, "quota": 710.0, "gialla": 1.8, "arancione": 2.6, "rossa": 3.5, "fonte": "Protezione Civile Basilicata", "scenario": "verde"},
            {"codice": "BAS_BASENTO_METAPONTO", "nome": "Basento a Metaponto", "fiume": "Basento", "regione": "Basilicata", "bacino": "APPENNINO_MERID", "lon": 16.8120, "lat": 40.3810, "quota": 5.0, "gialla": 3.2, "arancione": 4.5, "rossa": 5.8, "fonte": "Protezione Civile Basilicata", "scenario": "verde"},
            {"codice": "BAS_BRADANO_MATERA", "nome": "Bradano a San Giuliano (Matera)", "fiume": "Bradano", "regione": "Basilicata", "bacino": "APPENNINO_MERID", "lon": 16.6080, "lat": 40.6680, "quota": 105.0, "gialla": 2.8, "arancione": 4.0, "rossa": 5.2, "fonte": "Protezione Civile Basilicata", "scenario": "verde"},
            {"codice": "BAS_AGRI_POLICORO", "nome": "Agri a Policoro", "fiume": "Agri", "regione": "Basilicata", "bacino": "APPENNINO_MERID", "lon": 16.6710, "lat": 40.2110, "quota": 12.0, "gialla": 3.0, "arancione": 4.2, "rossa": 5.6, "fonte": "Protezione Civile Basilicata", "scenario": "verde"},
            {"codice": "BAS_SINNI_SENISE", "nome": "Sinni a Senise", "fiume": "Sinni", "regione": "Basilicata", "bacino": "APPENNINO_MERID", "lon": 16.2780, "lat": 40.1410, "quota": 220.0, "gialla": 2.5, "arancione": 3.6, "rossa": 4.8, "fonte": "Protezione Civile Basilicata", "scenario": "verde"},

            # --- CALABRIA ---
            {"codice": "CAL_CRATI_COSENZA", "nome": "Crati a Cosenza", "fiume": "Crati", "regione": "Calabria", "bacino": "APPENNINO_MERID", "lon": 16.2550, "lat": 39.3010, "quota": 235.0, "gialla": 2.8, "arancione": 4.0, "rossa": 5.2, "fonte": "ARPACAL Calabria", "scenario": "verde"},
            {"codice": "CAL_CRATI_SIBARI", "nome": "Crati a Cassano all'Ionio (Sibari)", "fiume": "Crati", "regione": "Calabria", "bacino": "APPENNINO_MERID", "lon": 16.4850, "lat": 39.7180, "quota": 10.0, "gialla": 4.5, "arancione": 6.0, "rossa": 7.5, "fonte": "ARPACAL Calabria", "scenario": "arancione"},
            {"codice": "CAL_NETO_CROTONE", "nome": "Neto a Crotone", "fiume": "Neto", "regione": "Calabria", "bacino": "APPENNINO_MERID", "lon": 17.1310, "lat": 39.0830, "quota": 15.0, "gialla": 3.0, "arancione": 4.5, "rossa": 6.0, "fonte": "ARPACAL Calabria", "scenario": "verde"},
            {"codice": "CAL_SAVUTO_NOCERA", "nome": "Savuto a Nocera Terinese", "fiume": "Savuto", "regione": "Calabria", "bacino": "APPENNINO_MERID", "lon": 16.1410, "lat": 39.0350, "quota": 18.0, "gialla": 2.5, "arancione": 3.8, "rossa": 5.0, "fonte": "ARPACAL Calabria", "scenario": "verde"},
            {"codice": "CAL_AMATO_LAMEZIA", "nome": "Amato a Lamezia Terme", "fiume": "Amato", "regione": "Calabria", "bacino": "APPENNINO_MERID", "lon": 16.3150, "lat": 38.9620, "quota": 30.0, "gialla": 2.2, "arancione": 3.2, "rossa": 4.4, "fonte": "ARPACAL Calabria", "scenario": "verde"},

            # --- SICILIA ---
            {"codice": "SIC_SIMETO_PATERNO", "nome": "Simeto a Paternò", "fiume": "Simeto", "regione": "Sicilia", "bacino": "SICILIA", "lon": 14.9010, "lat": 37.5680, "quota": 160.0, "gialla": 2.5, "arancione": 3.8, "rossa": 5.0, "fonte": "Regione Siciliana - SIAS", "scenario": "verde"},
            {"codice": "SIC_SIMETO_CATANIA", "nome": "Simeto a Catania (Foce Simeto)", "fiume": "Simeto", "regione": "Sicilia", "bacino": "SICILIA", "lon": 15.0810, "lat": 37.4010, "quota": 2.0, "gialla": 3.0, "arancione": 4.2, "rossa": 5.5, "fonte": "Regione Siciliana - SIAS", "scenario": "giallo"},
            {"codice": "SIC_ALCANTARA_NAXOS", "nome": "Alcantara a Giardini Naxos", "fiume": "Alcantara", "regione": "Sicilia", "bacino": "SICILIA", "lon": 15.2710, "lat": 37.8280, "quota": 15.0, "gialla": 2.0, "arancione": 3.0, "rossa": 4.0, "fonte": "Regione Siciliana - SIAS", "scenario": "verde"},
            {"codice": "SIC_SALSO_LICATA", "nome": "Salso / Imera a Licata", "fiume": "Salso", "regione": "Sicilia", "bacino": "SICILIA", "lon": 13.9380, "lat": 37.1050, "quota": 5.0, "gialla": 3.2, "arancione": 4.6, "rossa": 6.0, "fonte": "Regione Siciliana - SIAS", "scenario": "verde"},
            {"codice": "SIC_PLATANI_RIBERA", "nome": "Platani a Ribera", "fiume": "Platani", "regione": "Sicilia", "bacino": "SICILIA", "lon": 13.2650, "lat": 37.4980, "quota": 30.0, "gialla": 2.8, "arancione": 4.0, "rossa": 5.2, "fonte": "Regione Siciliana - SIAS", "scenario": "verde"},
            {"codice": "SIC_BELICE_CASTELV", "nome": "Belice a Castelvetrano / Selinunte", "fiume": "Belice", "regione": "Sicilia", "bacino": "SICILIA", "lon": 12.8350, "lat": 37.5850, "quota": 8.0, "gialla": 2.6, "arancione": 3.8, "rossa": 5.0, "fonte": "Regione Siciliana - SIAS", "scenario": "verde"},

            # --- SARDEGNA ---
            {"codice": "SAR_TIRSO_ORISTANO", "nome": "Tirso ad Oristano", "fiume": "Tirso", "regione": "Sardegna", "bacino": "SARDEGNA", "lon": 8.5910, "lat": 39.9050, "quota": 8.0, "gialla": 3.0, "arancione": 4.5, "rossa": 6.0, "fonte": "ARPAS Sardegna", "scenario": "verde"},
            {"codice": "SAR_TIRSO_FORDONG", "nome": "Tirso a Fordongianus", "fiume": "Tirso", "regione": "Sardegna", "bacino": "SARDEGNA", "lon": 8.8110, "lat": 39.9950, "quota": 32.0, "gialla": 2.5, "arancione": 3.8, "rossa": 5.0, "fonte": "ARPAS Sardegna", "scenario": "verde"},
            {"codice": "SAR_FLUMENDOSA_MURAV", "nome": "Flumendosa a Muravera", "fiume": "Flumendosa", "regione": "Sardegna", "bacino": "SARDEGNA", "lon": 9.5710, "lat": 39.4210, "quota": 10.0, "gialla": 3.5, "arancione": 5.0, "rossa": 6.5, "fonte": "ARPAS Sardegna", "scenario": "verde"},
            {"codice": "SAR_COGHINAS_STA_MARIA", "nome": "Coghinas a Santa Maria Coghinas", "fiume": "Coghinas", "regione": "Sardegna", "bacino": "SARDEGNA", "lon": 8.8680, "lat": 40.9050, "quota": 15.0, "gialla": 3.2, "arancione": 4.5, "rossa": 5.8, "fonte": "ARPAS Sardegna", "scenario": "giallo"},
            {"codice": "SAR_CEDRINO_OROSEI", "nome": "Cedrino ad Orosei", "fiume": "Cedrino", "regione": "Sardegna", "bacino": "SARDEGNA", "lon": 9.6920, "lat": 40.3810, "quota": 18.0, "gialla": 2.5, "arancione": 3.8, "rossa": 5.0, "fonte": "ARPAS Sardegna", "scenario": "verde"},
            {"codice": "SAR_TEMO_BOSA", "nome": "Temo a Bosa", "fiume": "Temo", "regione": "Sardegna", "bacino": "SARDEGNA", "lon": 8.4980, "lat": 40.2980, "quota": 4.0, "gialla": 2.0, "arancione": 2.8, "rossa": 3.8, "fonte": "ARPAS Sardegna", "scenario": "verde"},
        ]

        print(f"-> Inserimento/Aggiornamento di {len(stazioni_fiumi)} stazioni fluviali in PostGIS...")

        stazioni_db = []
        for s in stazioni_fiumi:
            point_wkt = f"SRID=4326;POINT({s['lon']} {s['lat']})"
            reg_id = regioni_map[s["regione"]].id if s["regione"] in regioni_map else None
            bac_id = bacini_map[s["bacino"]].id if s["bacino"] in bacini_map else None

            # Upsert stazione
            upsert_staz_sql = """
            INSERT INTO stazioni (
                codice_stazione, nome, fiume, regione_id, bacino_id, posizione,
                quota_zero_idrometrico, soglia_allerta_gialla, soglia_allerta_arancione, soglia_allerta_rossa,
                fonte_dati, attiva, created_at, updated_at
            ) VALUES (
                :codice, :nome, :fiume, :regione_id, :bacino_id,
                ST_GeomFromEWKT(:pos),
                :quota, :gialla, :arancione, :rossa,
                :fonte, true, NOW(), NOW()
            )
            ON CONFLICT (codice_stazione)
            DO UPDATE SET
                nome = EXCLUDED.nome,
                fiume = EXCLUDED.fiume,
                regione_id = EXCLUDED.regione_id,
                bacino_id = EXCLUDED.bacino_id,
                posizione = EXCLUDED.posizione,
                quota_zero_idrometrico = EXCLUDED.quota_zero_idrometrico,
                soglia_allerta_gialla = EXCLUDED.soglia_allerta_gialla,
                soglia_allerta_arancione = EXCLUDED.soglia_allerta_arancione,
                soglia_allerta_rossa = EXCLUDED.soglia_allerta_rossa,
                fonte_dati = EXCLUDED.fonte_dati,
                updated_at = NOW()
            RETURNING id;
            """
            st_id = session.execute(
                text(upsert_staz_sql),
                {
                    "codice": s["codice"],
                    "nome": s["nome"],
                    "fiume": s["fiume"],
                    "regione_id": reg_id,
                    "bacino_id": bac_id,
                    "pos": point_wkt,
                    "quota": s["quota"],
                    "gialla": s["gialla"],
                    "arancione": s["arancione"],
                    "rossa": s["rossa"],
                    "fonte": s["fonte"],
                }
            ).scalar()
            stazioni_db.append((st_id, s))

        session.commit()
        print(f"-> {len(stazioni_db)} stazioni salvate con coordinate geografiche.")

        # 4. Generazione serie temporali realistiche (ultime 48 ore) per ciascuna stazione
        now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        total_meas = 0

        print("-> Generazione serie temporali idrometriche delle ultime 48 ore...")

        meas_upsert_sql = """
        INSERT INTO misurazioni (stazione_id, timestamp, livello_idrometrico, portata, stato_allerta, validato, created_at)
        VALUES (:stazione_id, :timestamp, :livello, :portata, :stato, true, NOW())
        ON CONFLICT (stazione_id, timestamp)
        DO UPDATE SET
            livello_idrometrico = EXCLUDED.livello_idrometrico,
            portata = EXCLUDED.portata,
            stato_allerta = EXCLUDED.stato_allerta;
        """

        for st_id, s_info in stazioni_db:
            gialla = s_info["gialla"]
            arancione = s_info["arancione"]
            rossa = s_info["rossa"]
            scenario = s_info["scenario"]

            if scenario == "rosso":
                peak_target = rossa + 0.25
            elif scenario == "arancione":
                peak_target = arancione + 0.2
            elif scenario == "giallo":
                peak_target = gialla + 0.15
            else:
                peak_target = gialla * 0.55

            for h in range(48, -1, -1):
                t = now - timedelta(hours=h)
                # Calcola curva realistica con onda di piena a metà periodo
                factor = 0.75 + 0.25 * (1.0 - abs(20 - h) / 28.0)
                noise = random.uniform(-0.06, 0.06)
                livello = round(max(0.1, (peak_target * factor) + noise), 2)
                portata = round(livello * random.uniform(60.0, 160.0), 1)

                if livello >= rossa:
                    stato = "rosso"
                elif livello >= arancione:
                    stato = "arancione"
                elif livello >= gialla:
                    stato = "giallo"
                else:
                    stato = "verde"

                session.execute(
                    text(meas_upsert_sql),
                    {
                        "stazione_id": st_id,
                        "timestamp": t,
                        "livello": livello,
                        "portata": portata,
                        "stato": stato
                    }
                )
                total_meas += 1

        session.commit()
        print(f"=== SEED COMPLETATO CON SUCCESSO! ===")
        print(f"Stazioni totali nel database: {len(stazioni_db)}")
        print(f"Misurazioni storiche caricate: {total_meas}")

    except Exception as exc:
        session.rollback()
        print(f"Errore nel seed: {exc}")
        raise exc
    finally:
        session.close()


if __name__ == "__main__":
    seed_all_italian_rivers()
