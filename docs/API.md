# Streamlet Connector API Documentation

## Přehled

API poskytuje přístup k databázi filmů, seriálů a možnost streamování video souborů.

**Base URL**: `http://localhost:5000/api`

## Spuštění API serveru

### Samostatný API server (bez UI)
```bash
python run_api.py
```

Nebo s vlastním hostem a portem:
```bash
python run_api.py --host 0.0.0.0 --port 8080
```

### S GUI aplikací
API se automaticky spustí při běhu aplikace v režimu GUI:
```bash
python main.py
```

### Background režim
```bash
python main.py --background
```

## Endpointy

### 1. Seznam všech filmů
**GET** `/api/movies`

Vrací seznam všech filmů se základními informacemi.

**Response:**
```json
[
  {
    "id": 550,
    "title": "Fight Club",
    "poster": "/path/to/poster.jpg",
    "rating": 8.4
  },
  ...
]
```

**Pole:**
- `id` (int): TMDB ID filmu
- `title` (string): Název filmu
- `poster` (string): Cesta k posteru (lokální nebo TMDB URL)
- `rating` (float): Hodnocení 0-10

---

### 2. Seznam všech seriálů
**GET** `/api/tv-shows`

Vrací seznam všech TV seriálů se základními informacemi.

**Response:**
```json
[
  {
    "id": 1396,
    "title": "Breaking Bad",
    "poster": "/path/to/poster.jpg",
    "rating": 9.2
  },
  ...
]
```

**Pole:**
- `id` (int): TMDB ID seriálu
- `title` (string): Název seriálu
- `poster` (string): Cesta k posteru
- `rating` (float): Hodnocení 0-10

---

### 3. Detail filmu
**GET** `/api/movie/<tmdb_id>`

Vrací kompletní informace o filmu podle TMDB ID.

**Parametry:**
- `tmdb_id` (int): TMDB ID filmu

**Response:**
```json
{
  "id": 550,
  "title": "Fight Club",
  "original_title": "Fight Club",
  "release_date": "1999-10-15",
  "overview": "A ticking-time-bomb insomniac...",
  "poster_path": "/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg",
  "backdrop_path": "/fCayJrkfRaCRCTh8GqN30f8oyQF.jpg",
  "local_poster_path": "C:/dev/streamlet_connector/data/images/550_poster_xxx.jpg",
  "local_backdrop_path": "C:/dev/streamlet_connector/data/images/550_backdrop_xxx.jpg",
  "genres": ["Drama"],
  "runtime": 139,
  "vote_average": 8.4,
  "file_path": "//192.168.0.250/Filmy/Fight Club (1999).mkv",
  "year": "1999",
  "internal_id": 42
}
```

**Status kódy:**
- `200`: Úspěch
- `404`: Film nenalezen

---

### 4. Detail seriálu
**GET** `/api/tv-show/<tmdb_id>`

Vrací kompletní informace o seriálu podle TMDB ID.

**Parametry:**
- `tmdb_id` (int): TMDB ID seriálu

**Response:**
```json
{
  "id": 1396,
  "name": "Breaking Bad",
  "original_name": "Breaking Bad",
  "first_air_date": "2008-01-20",
  "overview": "When Walter White...",
  "poster_path": "/...",
  "backdrop_path": "/...",
  "local_poster_path": "C:/dev/streamlet_connector/data/images/1396_poster_xxx.jpg",
  "local_backdrop_path": "C:/dev/streamlet_connector/data/images/1396_backdrop_xxx.jpg",
  "genres": ["Drama", "Crime"],
  "number_of_seasons": 5,
  "number_of_episodes": 62,
  "vote_average": 9.2,
  "file_path": "//192.168.0.250/Serialy/Breaking Bad",
  "seasons": [...],
  "internal_id": 15
}
```

**Status kódy:**
- `200`: Úspěch
- `404`: Seriál nenalezen

---

### 5. Seznam všech video souborů (streamů)
**GET** `/api/streams`

Vrací seznam všech video souborů v databázi.

**Response:**
```json
[
  {
    "id": 0,
    "name": "Fight Club (1999).mkv",
    "type": "mkv",
    "size": 4589654123,
    "title": "Fight Club",
    "media_type": "movie",
    "tmdb_id": 550
  },
  {
    "id": 1,
    "name": "Inception (2010).mp4",
    "type": "mp4",
    "size": 3842156789,
    "title": "Inception",
    "media_type": "movie",
    "tmdb_id": 27205
  },
  ...
]
```

**Pole:**
- `id` (int): Interní ID pro přístup ke streamu
- `name` (string): Jméno souboru
- `type` (string): Typ souboru (mkv, mp4, avi, ...)
- `size` (int): Velikost v bytech
- `title` (string): Název filmu/seriálu
- `media_type` (string): "movie" nebo "tv_show"
- `tmdb_id` (int|null): TMDB ID nebo null

---

### 6. Stream/download video souboru
**GET** `/api/stream/<stream_id>`

Vrací video soubor pro streaming nebo download.

**Parametry:**
- `stream_id` (int): Interní ID ze seznamu streamů

**Response:**
- Video soubor (binární data)
- Content-Type podle typu souboru

**Použití:**
```html
<!-- Video player -->
<video controls>
  <source src="http://localhost:5000/api/stream/0" type="video/mp4">
</video>

<!-- Download link -->
<a href="http://localhost:5000/api/stream/0" download>Stáhnout film</a>
```

**Status kódy:**
- `200`: Úspěch
- `404`: Stream nenalezen nebo soubor neexistuje
- `500`: Chyba při čtení souboru

---

### 7. Informace o streamu
**GET** `/api/stream/<stream_id>/info`

Vrací informace o video souboru bez stahování.

**Parametry:**
- `stream_id` (int): Interní ID streamu

**Response:**
```json
{
  "id": 0,
  "path": "//192.168.0.250/Filmy/Fight Club (1999).mkv",
  "name": "Fight Club (1999).mkv",
  "type": "mkv",
  "size": 4589654123,
  "url": "/api/stream/0"
}
```

**Status kódy:**
- `200`: Úspěch
- `404`: Stream nenalezen

---

### 8. Health check
**GET** `/api/health`

Kontrola stavu API serveru a statistiky databáze.

**Response:**
```json
{
  "status": "ok",
  "total_items": 157,
  "movies": 105,
  "tv_shows": 52
}
```

## Příklady použití

### cURL

```bash
# Seznam filmů
curl http://localhost:5000/api/movies

# Detail filmu
curl http://localhost:5000/api/movie/550

# Seznam streamů
curl http://localhost:5000/api/streams

# Stáhnout video
curl http://localhost:5000/api/stream/0 -o movie.mkv

# Health check
curl http://localhost:5000/api/health
```

### Python

```python
import requests

# Získat všechny filmy
response = requests.get('http://localhost:5000/api/movies')
movies = response.json()

for movie in movies:
    print(f"{movie['title']} - Rating: {movie['rating']}")

# Získat detail filmu
movie_id = 550
response = requests.get(f'http://localhost:5000/api/movie/{movie_id}')
movie = response.json()
print(f"Overview: {movie['overview']}")

# Stream video
stream_id = 0
stream_url = f'http://localhost:5000/api/stream/{stream_id}'
# Použij ve video playeru nebo stáhni:
response = requests.get(stream_url, stream=True)
with open('downloaded_movie.mkv', 'wb') as f:
    for chunk in response.iter_content(chunk_size=8192):
        f.write(chunk)
```

### JavaScript (fetch)

```javascript
// Načíst filmy
fetch('http://localhost:5000/api/movies')
  .then(response => response.json())
  .then(movies => {
    movies.forEach(movie => {
      console.log(`${movie.title} - ${movie.rating}/10`);
    });
  });

// Detail filmu
const movieId = 550;
fetch(`http://localhost:5000/api/movie/${movieId}`)
  .then(response => response.json())
  .then(movie => {
    console.log('Title:', movie.title);
    console.log('Overview:', movie.overview);
    console.log('Genres:', movie.genres.join(', '));
  });

// Video player
const streamId = 0;
const videoElement = document.getElementById('player');
videoElement.src = `http://localhost:5000/api/stream/${streamId}`;
```

## CORS

Pro přístup z webových aplikací na jiných doménách můžete potřebovat povolit CORS. To lze udělat úpravou `src/api.py`:

```python
from flask_cors import CORS

# V __init__ metodě:
CORS(self.app)
```

Instalace:
```bash
pip install flask-cors
```

## Poznámky

- **Velikosti souborů**: API neomezuje velikost streamovaných souborů
- **Výkon**: Pro produkční použití doporučujeme nginx nebo jiný reverse proxy
- **Bezpečnost**: API nemá autentizaci - použijte firewall nebo VPN pro bezpečný přístup
- **Databáze**: API používá `data/media_db.json` - ujistěte se, že máte naskenovaná data
