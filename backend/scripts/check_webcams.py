import urllib.request
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.core.database import SyncSessionLocal
from sqlalchemy import text

def check_all_db_webcams():
    session = SyncSessionLocal()
    try:
        results = session.execute(text("SELECT id, codice_stazione, nome, fiume, webcam_url FROM stazioni WHERE webcam_url IS NOT NULL")).fetchall()
        print(f"Trovate {len(results)} stazioni con webcam_url configurato nel database.\n")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        for row in results:
            st_id, cod, nome, fiume, url = row
            print(f"Stazione #{st_id} - {nome} ({fiume}) [{cod}]:\n  URL: {url}")
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=5) as response:
                    status = response.status
                    ct = response.headers.get('Content-Type', '')
                    raw = response.read()
                    content = raw.decode('utf-8', errors='ignore')
                    
                    if "youtube.com" in url:
                        if "errorScreen" in content or "playerInterstitialRenderer" in content or "Errore 153" in content:
                            print(f"  -> RISULTATO: [NON FUNZIONANTE] YouTube segnala errore/canale inesistente o stream offline (HTTP {status}).\n")
                        else:
                            print(f"  -> RISULTATO: [FUNZIONANTE] Flusso YouTube attivo (HTTP {status}).\n")
                    elif url.endswith(".jpg") or url.endswith(".jpeg") or url.endswith(".png"):
                        if not ct.startswith("image/"):
                            print(f"  -> RISULTATO: [NON FUNZIONANTE] Estensione immagine ma il server ha restituito HTML ({ct}, {len(raw)} byte).\n")
                        else:
                            print(f"  -> RISULTATO: [FUNZIONANTE] Immagine valida ricevuta ({len(raw)} byte).\n")
                    else:
                        print(f"  -> RISULTATO: HTTP {status}, Content-Type: {ct}\n")
            except Exception as e:
                print(f"  -> RISULTATO: [ERRORE DI RETE / 404] {e}\n")
                
    finally:
        session.close()

if __name__ == '__main__':
    check_all_db_webcams()
