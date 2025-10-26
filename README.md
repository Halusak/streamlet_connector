# Streamlet Connector

Streamlet Connector je metadata parser pro filmy a seriály, který slouží jako most mezi vašimi lokálními mediálními soubory a streamovacími platformami. Projekt poskytuje REST API pro správu mediální databáze, vyhledávání metadat přes TMDB a webové rozhraní pro snadnou správu.

## Funkce

- **Automatické skenování médií**: Skenuje zadané složky a detekuje filmy a seriály
- **TMDB integrace**: Načítá metadata, plakáty a další informace z The Movie Database
- **REST API**: Kompletní API pro přístup k datům médií
- **Web UI**: Uživatelsky přívětivé webové rozhraní pro správu
- **Streamlet kompatibilita**: Kompatibilní s Streamlet platformou pro streamování
- **Konfigurovatelné**: Široké možnosti konfigurace přes JSON soubory

## Požadavky

- Python 3.8+
- TMDB API klíč (zdarma na [themoviedb.org](https://www.themoviedb.org/settings/api))

## Instalace

1. **Klonujte repozitář:**
   ```bash
   git clone https://github.com/yourusername/streamlet_connector.git
   cd streamlet_connector
   ```

2. **Nainstalujte závislosti:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Konfigurace:**
   - Zkopírujte `config/config.json` a upravte podle potřeb
   - Zadejte váš TMDB API klíč do konfiguračního souboru

4. **Spusťte aplikaci:**
   ```bash
   python run_api.py
   ```

   Aplikace bude dostupná na `http://localhost:5000`

## Použití

### Webové rozhraní

Otevřete prohlížeč a přejděte na `http://localhost:5000/ui` pro přístup k webovému rozhraní.

### API Endpoints

Podrobnou dokumentaci API najdete v [docs/API.md](docs/API.md).

Hlavní endpointy:
- `GET /api/movies` - Seznam filmů
- `GET /api/tv-shows` - Seznam seriálů
- `GET /api/movie/{id}` - Detaily filmu
- `GET /api/search` - Vyhledávání

### Příkazová řádka

```bash
# Spuštění s vlastním hostem a portem
python run_api.py --host 0.0.0.0 --port 8000
```

## Konfigurace

Upravte soubor `config/config.json`:

```json
{
  "folders_to_scan": ["/path/to/movies", "/path/to/series"],
  "tmdb_api_key": "your_tmdb_api_key_here",
  "tmdb_language": "cs-CZ",
  "scan_interval": 3600
}
```

## Vývoj

### Struktura projektu

```
streamlet_connector/
├── src/
│   ├── api.py              # Hlavní Flask API
│   ├── tmdb_client.py      # TMDB API klient
│   ├── media_database.py   # Správa databáze médií
│   ├── scanner.py          # Skenování složek
│   └── progress_tracker.py # Sledování průběhu
├── config/
│   └── config.json         # Konfigurace
├── data/
│   └── media_db.json       # Databáze médií
├── templates/
│   └── ui.html             # Webové rozhraní
├── docs/                   # Dokumentace
└── requirements.txt        # Python závislosti
```

### Spuštění v režimu vývoje

```bash
export FLASK_ENV=development
python run_api.py
```

## Přispívání

1. Forkněte projekt
2. Vytvořte feature branch (`git checkout -b feature/AmazingFeature`)
3. Commitněte změny (`git commit -m 'Add some AmazingFeature'`)
4. Pushněte do branch (`git push origin feature/AmazingFeature`)
5. Otevřete Pull Request

## Licence

Tento projekt je licencován pod MIT License - viz soubor [LICENSE](LICENSE) pro detaily.

## Kontakt

- Autor: Haluška
- Projekt: [Streamlet Connector](https://www.streamlet.info/)
- Repository: [GitHub](https://github.com/Haluak/streamlet_connector)