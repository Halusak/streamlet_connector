# Rychlý start - API Server

## Krok 1: Ujistěte se, že máte data v databázi

Spusťte GUI aplikaci a naskenujte média:
```bash
python main.py
```

V aplikaci:
1. Přejděte na záložku **Settings**
2. Zkontrolujte složky pro skenování
3. Přejděte na záložku **Media**
4. Klikněte na **Scan Folders**

Počkejte, až se dokončí skenování a stažení metadat z TMDB.

## Krok 2: Spusťte API server

```bash
python run_api.py
```

API server bude dostupný na: **http://localhost:5000**

## Krok 3: Otevřete demo v prohlížeči

Jednoduše otevřete v prohlížeči:

```
http://localhost:5000
```

nebo

```
http://localhost:5000/demo
```

**Hotovo!** Demo aplikace je nyní přímo součástí API serveru, takže není potřeba řešit CORS ani otevírat HTML soubory.

### Vlastní host/port

Pro přístup z jiných zařízení v síti:
```bash
python run_api.py --host 0.0.0.0 --port 8080
```

Pak otevřete: `http://192.168.x.x:8080` (vaše IP adresa)

### JavaScript příklad:

```javascript
// Načíst filmy
fetch('http://localhost:5000/api/movies')
  .then(r => r.json())
  .then(movies => console.log(movies));

// Přehrát video
const videoElement = document.getElementById('player');
videoElement.src = 'http://localhost:5000/api/stream/0';
```

### Python příklad:

```python
import requests

# Seznam filmů
movies = requests.get('http://localhost:5000/api/movies').json()

# Detail filmu
movie = requests.get('http://localhost:5000/api/movie/550').json()
print(movie['title'], movie['overview'])

# Stáhnout video
with open('movie.mkv', 'wb') as f:
    response = requests.get('http://localhost:5000/api/stream/0', stream=True)
    for chunk in response.iter_content(chunk_size=8192):
        f.write(chunk)
```

## Tipy

### CORS pro webové aplikace

Pokud chcete přistupovat k API z jiné domény, nainstalujte flask-cors:

```bash
pip install flask-cors
```

A přidejte do `src/api.py`:
```python
from flask_cors import CORS

# V __init__:
CORS(self.app)
```

### Přístup z mobilních zařízení

1. Spusťte server s `--host 0.0.0.0`
2. Zjistěte IP adresu počítače (např. `192.168.1.100`)
3. Na mobilu otevřete: `http://192.168.1.100:5000/api/movies`

### Bezpečnost

API nemá autentizaci! Pro produkční použití:
- Použijte firewall nebo VPN
- Přidejte API klíče nebo OAuth
- Zvažte použití HTTPS s reverse proxy (nginx)

## Kompletní dokumentace

Viz [API.md](API.md) pro detailní popis všech endpointů.
