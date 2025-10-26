## Streamlet Connector — API dokumentace

Tento dokument popisuje REST API implementované v `src/api.py` pro projekt Streamlet Connector.

Obsah:
- Přehled
- Spuštění serveru
- Základní URL
- Endpoints (popis, parametry, příklady)
- Datové struktury
- Poznámky a omezení

## Přehled

API poskytuje tyto hlavní funkce:
- Prohlížení lokální databáze mediálních souborů
- Vyhledávání a přiřazování metadat z TMDB
- Spuštění skenu složek pro nové mediální soubory
- Servírování lokálních obrázků a videí
- Základní webové UI dostupné na `/ui`

API je navrženo jako jednoduché REST rozhraní bez autentizace (lokální použití).

## Spuštění serveru

Spuštění aplikace ze základního adresáře projektu (PowerShell):

```powershell
python run_api.py
```

Po spuštění budou vypsány URL pro Web UI a API (výchozí: http://localhost:5000).

## Základní URL

Veškeré endpointy začínají kořenem serveru, například:
- Web UI: `/ui` nebo `/`
- API root: `/api`

Poznámka: V dokumentaci jsou uváděny relativní cesty (např. `/api/items`).

## Endpoints

Níže jsou endpointy se souhrnem, parametry a příklady.

### Web UI

- GET /ui
- GET /

Popis: Vrátí jednoduché webové rozhraní (HTML). Šablona se načítá z `templates/ui.html`, pokud existuje, jinak se vrátí zabudované základní HTML.

### Získání všech položek

- GET /api/items

Popis: Vrátí seznam všech mediálních položek známých databázi. Obsahuje i položky bez metadat.

Response: 200 OK, JSON pole objektů s následujícími poli (přehled):
- internal_id: interní index v paměti
- path: absolutní cesta k souboru
- title: název (souboru nebo extrahovaný)
- display_title: název k zobrazení (z metadat nebo title)
- type: 'movie' nebo 'tv_show' (může být None)
- has_metadata: boolean
- tmdb_id, poster, backdrop, rating, year, overview — pokud jsou metadata dostupná

Příklad (skrácený):

```json
[{
	"internal_id": 0,
	"path": "C:/media/Film.mp4",
	"title": "Film",
	"display_title": "Film (2020)",
	"type": "movie",
	"has_metadata": true,
	"tmdb_id": 12345,
	"poster": "poster.jpg",
	"rating": 7.2
}]
```

### TMDB vyhledávání

- GET /api/search

Parametry (query string):
- query (required): řetězec pro hledání
- type (optional): 'movie' (default) nebo 'tv'

Popis: Vyhledá v TMDB filmy nebo seriály a vrátí až 10 výsledků.

Příklad requestu:

```
GET /api/search?query=Inception&type=movie
```

Odpověď: 200 OK, pole objektů s poli `tmdb_id`, `title`, `year`, `overview`, `poster_path`, `rating`.

Chyby:
- 400 pokud chybí `query` nebo je `type` neplatný.
- 500 při interní chybě (např. problém s TMDB klientem).

### Přiřazení metadat k položce

- POST /api/assign-metadata

Tělo (JSON):
- internal_id (int) — interní index položky v databázi
- tmdb_id (int) — TMDB ID z výsledků vyhledávání
- type (string) — 'movie' nebo 'tv' / 'tv_show'

Popis: Načte podrobné metadata z TMDB (podle typu), přiřadí je k položce, stáhne lokální obrázky (poster/backdrop), uloží do databáze.

Odpověď: 200 OK při úspěchu: {"success": true, "message": "Metadata assigned successfully"}

Chyby:
- 400 pokud chybí povinné parametry nebo je `type` neplatný.
- 404 pokud `internal_id` není platné.
- 500 při interní chybě (např. selhání TMDB nebo uložení).

### Nastavení aplikace

- GET /api/settings
	- Popis: Vrátí aktuální konfiguraci (obsah config.json načtený při startu nebo default hodnoty).

- POST /api/settings
	- Tělo (JSON): možné klíče
		- folders_to_scan: pole string (cesty)
		- tmdb_api_key: string
		- tmdb_language: string
		- scan_interval: int (v sekundách)
	- Popis: Uloží konfiguraci do `config/config.json`, aktualizuje TMDB klienta a scanner.
	- Odpověď: 200 OK při úspěchu nebo 500 při selhání uložení.

### Spuštění skenu

- POST /api/scan

Popis: Spustí sken složek (konfigurovaných v `folders_to_scan`). Pokud je TMDB klient nakonfigurován, provede i enrich (okamžité dotazování TMDB během skenu). Odstraní chybějící soubory z databáze a přidá nové položky.

Odpověď: 200 OK s přehledem výsledků (příklad):

```json
{
	"success": true,
	"total_found": 42,
	"new_items": 5,
	"removed_items": 2,
	"enriched_with_metadata": 18,
	"message": "Found 42 items, added 5 new, removed 2 missing"
}
```

Chyby: 500 při interním selhání.

### Stav postupu skenu

- GET /api/progress

Popis: Vrátí objekt s průběhem skenu. Implementace závisí na `ProgressTracker` v kódu.

Odpověď: 200 OK s JSONem (struktura výsledku je definována v `ProgressTracker.get_progress()`).

### Správa databáze

- POST /api/database/clear

Popis: Smaže celou databázi a všechny lokální obrázky (data/images). Použití riskantní — nevratné.

Odpověď: 200 OK při úspěchu, nebo 500 při selhání.

### Servírování obrázků

- GET /api/images/<filename>

Popis: Servíruje lokální images uložené ve `data/images`.

Chyby: 404 pokud obrázek neexistuje.

### Legacy endpointy — přehled (kompatibilita)

- GET /api/movies
	- Vrátí pole všech filmů (ty, které mají `type == 'movie'` a metadata).
	- Každý prvek obsahuje: `id` (TMDB id), `title`, `poster`, `rating`.

- GET /api/tv-shows
	- Vrátí pole všech TV show (ty, které mají `type == 'tv_show'`).

- GET /api/movie/<int:tmdb_id>
	- Vrátí detailní metadata pro film s daným TMDB ID, včetně `local_poster_path`, `local_backdrop_path`, `file_path`, `year`, a `internal_id`.
	- 404 pokud není nalezen.

- GET /api/tv-show/<int:tmdb_id>
	- Vrátí detailní metadata pro TV show (včetně seznamu sezon `seasons` a `internal_id`).
	- 404 pokud není nalezen.

### Streamy (video soubory)

- GET /api/streams
	- Vrátí seznam všech video souborů nalezených v databázi s informacemi: `id` (interní index), `name`, `type` (přípona), `size`, `title`, `media_type`, `tmdb_id`.

- GET /api/stream/<int:stream_id>
	- Vrátí přímo video soubor (posílá soubor přes Flask `send_file`) pro streamování nebo stažení.
	- 404 pokud `stream_id` neexistuje nebo soubor chybí.

- GET /api/stream/<int:stream_id>/info
	- Vrátí metadata o souboru bez stažení: `id`, `path`, `name`, `type`, `size`, `url` (odkaz na `/api/stream/<id>`).

### Health check

- GET /api/health
	- Vrací status aplikace a souhrn počtu položek:
		- status: 'ok'
		- total_items
		- movies
		- tv_shows

## Datové struktury (přehled)

Media item (v databázi) — minimální relevantní pole:

- path: string — absolutní cesta k souboru
- title: string — rozumný název (např. název souboru nebo rozparsovaný název)
- type: 'movie' nebo 'tv_show' (volitelné)
- metadata: objekt — kompletní TMDB metadata (pokud přiřazena)
- local_poster_path: string — název lokálního souboru s posterem uloženého v `data/images`
- local_backdrop_path: string — název lokálního souboru s backdropem

TMDB metadata: struktura odpovídá datům vráceným TMDB API klientem (`tmdb_client`). Může obsahovat `id`, `title`/`name`, `overview`, `poster_path`, `backdrop_path`, `vote_average`, `release_date`/`first_air_date` atd.

## Příklady použití (curl)

Vyhledání filmů s názvem "Inception":

```bash
curl -s "http://localhost:5000/api/search?query=Inception&type=movie"
```

Přiřazení metadat (příklad):

```bash
curl -X POST "http://localhost:5000/api/assign-metadata" \
	-H "Content-Type: application/json" \
	-d '{"internal_id":0, "tmdb_id":27205, "type":"movie"}'
```

Získání seznamu streamů:

```bash
curl "http://localhost:5000/api/streams"
```

Stažení nebo stream video souboru s ID 3 (otevře soubor v prohlížeči nebo přehraje v přehrávači):

```bash
curl -v "http://localhost:5000/api/stream/3" --output "video.mp4"
```

## Chyby a stavové kódy

- 200 — OK (úspěšné odpovědi)
- 400 — špatný požadavek (chybějící parametry nebo nevalidní hodnoty)
- 404 — nenalezeno (položka/databáze/soubor)
- 500 — interní chyba serveru (např. problém s uložením, TMDB, čtením souboru)

V případě 500 endpointy vrací JSON s `error` polem popisujícím chybu.

## Poznámky a doporučení

- API nemá implementovanou autentizaci — doporučeno omezit přístup (např. běžet za reverzním proxy s autentizací) pokud bude vystaveno do sítě.
- Operace jako `/api/database/clear` jsou nevratné — používejte s opatrností.
- Cesty k obrázkům vracené v polích jako `poster` jsou pouze názvy souborů; k jejich načtení použijte `/api/images/<filename>`.

## Další kroky / vylepšení

- Přidat autentizaci a autorizaci
- Přidat paging / filtrování pro `/api/items` a `/api/streams`
- Přidat detailní příklady odpovědí pro každou chybu
- Přidat testy integrace pro hlavní endpointy

---

Soubor: `src/api.py` — dokumentované endpointy byly zdokumentovány výše.

Pokud chcete, mohu doplnit i auto-generované OpenAPI/Swagger schéma nebo připravit ukázkové Postman kolekce.
