# Streamlet Connector - Web UI Dokumentace

## Přehled

Streamlet Connector nyní obsahuje plnohodnotné webové uživatelské rozhraní na adrese `/ui`, které plně nahrazuje původní Python Tkinter UI. Veškeré ovládání a správa médií probíhá v prohlížeči.

## Spuštění

```bash
python run_api.py
```

Pak otevřete v prohlížeči: **http://localhost:5000/ui**

## Funkce Web UI

### 1. Databáze médií

**Funkce:**
- Zobrazení všech médií z databáze
- Filtrování podle typu (všechny/filmy/seriály/bez metadat)
- Vyhledávání v názvech a cestách
- Vizuální označení položek bez metadat (červený rámeček)

**Jak používat:**
1. Otevřete stránku "Databáze"
2. Použijte vyhledávací pole pro rychlé vyhledání
3. Klikněte na filtr (Vše/Filmy/Seriály/Bez metadat)
4. Klikněte na kartu média pro zobrazení detailů

### 2. Detail média

**Pro položky s metadaty:**
- Zobrazení posteru, názvu, roku, hodnocení
- Zobrazení popisu a žánrů
- Přehrávání videa přímo v prohlížeči
- Stažení souboru

**Pro položky bez metadat:**
- Zobrazení cesty k souboru
- Možnost přiřazení metadat z TMDB
- Tlačítko "Přiřadit metadata z TMDB"

### 3. Přiřazení metadat z TMDB

**Postup:**
1. Klikněte na položku bez metadat
2. Klikněte na "Přiřadit metadata z TMDB"
3. Vyberte typ (Film/Seriál)
4. Zadejte název do vyhledávání
5. Klikněte na "Hledat"
6. V seznamu výsledků vyberte správnou položku
7. Metadata se automaticky stáhnou a uloží

### 4. Nastavení

**TMDB Nastavení:**
- **API Klíč**: Váš TMDB API klíč pro stahování metadat
- **Jazyk**: Preferovaný jazyk pro metadata (cs-CZ, en-US, sk-SK, de-DE, fr-FR)

**Složky ke skenování:**
- Přidání/odebrání složek pro automatické skenování
- Podpora UNC cest (Windows): `\\\\server\\share`
- Podpora Linux/NAS cest: `/mnt/media`

**Skenování:**
- Tlačítko "Spustit skenování" zahájí automatické prohledání složek
- Po dokončení se zobrazí počet nalezených a přidaných položek
- Nové položky se automaticky objeví v databázi

## API Endpointy

Webové UI komunikuje s těmito API endpointy:

### Database
- `GET /api/items` - Vrátí všechny položky včetně těch bez metadat
- `GET /api/images/<path>` - Lokální obrázky (postery, backdrops)

### TMDB
- `GET /api/search?query=<text>&type=<movie|tv>` - Vyhledání v TMDB
- `POST /api/assign-metadata` - Přiřazení metadat k položce
  ```json
  {
    "internal_id": 0,
    "tmdb_id": 123456,
    "type": "movie"
  }
  ```

### Settings
- `GET /api/settings` - Načtení nastavení
- `POST /api/settings` - Uložení nastavení
  ```json
  {
    "tmdb_api_key": "...",
    "tmdb_language": "cs-CZ",
    "folders_to_scan": ["/mnt/movies"]
  }
  ```

### Scanning
- `POST /api/scan` - Spustí skenování složek

### Streaming (legacy)
- `GET /api/stream/<id>` - Streamování/stahování videa
- `GET /api/movies` - Seznam filmů
- `GET /api/tv-shows` - Seznam seriálů
- `GET /api/movie/<tmdb_id>` - Detail filmu
- `GET /api/tv-show/<tmdb_id>` - Detail seriálu

## Workflow

### První nastavení

1. Otevřete http://localhost:5000/ui
2. Přejděte na "Nastavení"
3. Zadejte TMDB API klíč
4. Vyberte preferovaný jazyk
5. Přidejte složky ke skenování
6. Klikněte "Uložit nastavení"
7. Klikněte "Spustit skenování"

### Správa metadat

1. Přejděte na "Databáze"
2. Klikněte na filtr "Bez metadat"
3. Pro každou položku:
   - Klikněte na kartu
   - Klikněte "Přiřadit metadata z TMDB"
   - Vyhledejte správný film/seriál
   - Vyberte ze seznamu výsledků

### Přehrávání

1. Najděte médium v databázi
2. Klikněte na kartu pro otevření detailu
3. Klikněte "Přehrát" pro přehrávání v prohlížeči
4. Nebo klikněte "Stáhnout" pro stažení souboru

## Technické detaily

### Frontend
- Čistý HTML5 + CSS3 + Vanilla JavaScript
- Žádné externí závislosti
- Responzivní design (desktop i mobil)
- Dark theme s #9DD8FF akcenty

### Backend
- Flask REST API
- Automatické ukládání do JSON databáze
- Stahování a cachování obrázků
- Podpora UNC cest a NAS

### Obrázky
- Automatické stahování posterů a backdrops z TMDB
- Lokální cache v `data/images/`
- Fallback na placeholder při chybě

## Troubleshooting

### Nefungují obrázky
- Zkontrolujte, že složka `data/images` existuje
- Zkontrolujte API klíč v nastavení
- Metadata musí být přiřazena, aby se obrázky stáhly

### Skenování nenalezne soubory
- Zkontrolujte formát cesty:
  - Windows UNC: `\\\\192.168.0.250\\Filmy`
  - Linux: `/mnt/movies`
- Zkontrolujte přístupová práva
- Podporované formáty: .mkv, .mp4, .avi, .mov, .wmv, .flv, .webm, .m4v

### Nepřehrává se video
- Zkontrolujte, že soubor existuje na cestě
- Některé prohlížeče nepodporují všechny video formáty
- Použijte "Stáhnout" jako alternativu

## Migrace ze staré verze

Pokud jste používali Tkinter UI (`src/ui.py`):
- Veškerá data z `data/media_db.json` zůstávají zachována
- Konfigurace v `config/config.json` se automaticky načte
- Staré UI můžete smazat, již se nepoužívá
- Web UI nabízí všechny funkce + nové (přiřazení metadat, přehrávání)

## Bezpečnost

⚠️ **VAROVÁNÍ**: Tento server je určen pro lokální síť!
- Běží na 0.0.0.0 (dostupný ze sítě)
- Není implementována autentizace
- Pro internet použijte reverse proxy s HTTPS a autentizací

## Výkon

- **Rychlost**: Velmi rychlé načítání díky cachování
- **Concurrency**: Flask běží s `threaded=True` pro paralelní požadavky
- **Streaming**: Podporuje Range requesty pro seek ve videu
- **Databáze**: JSON soubor, rychlý pro malé a střední kolekce (< 10000 položek)

## Budoucí vylepšení

Plánované funkce:
- [ ] Hromadné přiřazení metadat
- [ ] Editace metadat
- [ ] Filtrování podle žánrů
- [ ] Oblíbené položky
- [ ] Historie přehrávání
- [ ] Podpora více databází
- [ ] Export do formátů (Plex, Kodi)
