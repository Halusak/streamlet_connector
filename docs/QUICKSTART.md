# Quick Start Guide - Streamlet Connector Web UI

## 🚀 Spuštění za 2 minuty

### 1. Start serveru
```bash
python run_api.py
```

Uvidíte:
```
============================================================
Streamlet Connector API Server
============================================================
Database: 63 items loaded
Web UI: http://0.0.0.0:5000/ui
Server: http://0.0.0.0:5000
============================================================

💡 Otevřete v prohlížeči web UI:
   http://localhost:5000/ui
```

### 2. Otevřete v prohlížeči
```
http://localhost:5000/ui
```

---

## 📖 První použití

### Krok 1: Nastavení TMDB
1. Klikněte na "Nastavení" v horní liště
2. Zadejte váš TMDB API klíč
3. Vyberte jazyk (např. Čeština)
4. Klikněte "Uložit nastavení"

### Krok 2: Přidání složek
1. V sekci "Složky ke skenování"
2. Zadejte cestu (např. `\\\\192.168.0.250\\Filmy` nebo `/mnt/movies`)
3. Klikněte "Přidat"
4. Opakujte pro další složky
5. Klikněte "Uložit nastavení"

### Krok 3: Skenování
1. Klikněte "🔍 Spustit skenování"
2. Počkejte na dokončení (zobrazí se alert s výsledky)
3. Klikněte na "Databáze" v horní liště

### Krok 4: Prohlížení médií
1. V databázi uvidíte všechna nalezená média
2. Použijte filtry: Vše / Filmy / Seriály / Bez metadat
3. Použijte vyhledávací pole pro rychlé hledání
4. Klikněte na kartu pro detail

---

## 🎯 Hlavní funkce

### 📂 Prohlížení databáze
```
[Databáze] → [Vyberte filtr] → [Klikněte na kartu]
```
- **Vše**: Všechna média
- **Filmy**: Pouze filmy
- **Seriály**: Pouze seriály
- **Bez metadat**: Položky bez TMDB dat (červený rámeček)

### 🔍 Přiřazení metadat
```
[Klikněte na položku bez metadat] → [Přiřadit metadata z TMDB] → 
[Vyberte Film/Seriál] → [Zadejte název] → [Hledat] → 
[Vyberte výsledek ze seznamu]
```

Po výběru se automaticky:
- Stáhnou metadata z TMDB
- Stáhnou postery a backdrops
- Uloží do databáze
- Položka se objeví s daty

### ▶️ Přehrávání
```
[Klikněte na film/seriál] → [▶ Přehrát]
```
Video se otevře přímo v prohlížeči!

### ⬇️ Stahování
```
[Klikněte na film/seriál] → [⬇ Stáhnout]
```

---

## 💡 Tipy a triky

### Rychlé vyhledávání
- Zadejte text do vyhledávacího pole
- Vyhledává v názvech i cestách
- Funguje v kombinaci s filtry

### Filtrování bez metadat
1. Klikněte na "Bez metadat"
2. Uvidíte pouze položky s červeným rámečkem
3. Postupně jim přiřazujte metadata

### Klávesové zkratky
- **Enter** v TMDB vyhledávání = Spustí hledání
- **ESC** v modalu = Zavře modal (většina prohlížečů)
- **Klik mimo modal** = Zavře modal

### Batch processing
Pro rychlé zpracování položek bez metadat:
1. Filtr "Bez metadat"
2. Otevřete první položku
3. Přiřaďte metadata
4. Automaticky se aktualizuje
5. Otevřete další položku

---

## 🔧 Troubleshooting

### Nefungují obrázky
- ✅ Zkontrolujte TMDB API klíč v nastavení
- ✅ Metadata musí být přiřazena (přes "Přiřadit metadata z TMDB")
- ✅ Zkontrolujte, že složka `data/images/` existuje

### Skenování nenalezne soubory
- ✅ Formát cesty:
  - Windows: `C:\\Movies` nebo `\\\\server\\share`
  - Linux: `/mnt/movies` nebo `/media/nas/movies`
- ✅ Zkontrolujte přístupová práva
- ✅ Podporované formáty: mkv, mp4, avi, mov, wmv, flv, webm, m4v

### Video se nepřehrává
- ✅ Některé prohlížeče nepodporují všechny formáty
- ✅ Zkontrolujte, že soubor stále existuje
- ✅ Použijte "Stáhnout" jako alternativu
- ✅ Zkuste jiný prohlížeč (Chrome/Firefox/Edge)

### Server není dostupný z jiného zařízení
- ✅ Server běží na `0.0.0.0` (všechny síťové rozhraní)
- ✅ Najděte IP adresu serveru: `ipconfig` (Win) nebo `ifconfig` (Linux)
- ✅ Použijte `http://<IP_ADRESA>:5000/ui`
- ✅ Zkontrolujte firewall

---

## 🎨 Vzhled UI

### Barevné označení
- **Modrá (#9DD8FF)**: Primární barva, aktivní tlačítka
- **Černá (#0f0f0f)**: Pozadí
- **Červená**: Badge "Bez dat" a ohraničení

### Karty
- **Normální**: Modrý rámeček při hoveru
- **Bez metadat**: Červený přerušovaný rámeček

---

## 📱 Mobilní zařízení

Web UI funguje i na telefonech a tabletech!

### Přístup
```
http://<IP_SERVERU>:5000/ui
```

### Optimalizace
- Responzivní layout
- Dotykové ovládání
- Optimalizovaná velikost karet
- Scrollovací modaly

---

## ⚡ Pokročilé

### API přístup
Vše co dělá Web UI, můžete dělat i přes API:

```bash
# Všechny položky
curl http://localhost:5000/api/items

# Vyhledání v TMDB
curl "http://localhost:5000/api/search?query=Matrix&type=movie"

# Přiřazení metadat
curl -X POST http://localhost:5000/api/assign-metadata \
  -H "Content-Type: application/json" \
  -d '{"internal_id": 0, "tmdb_id": 603, "type": "movie"}'
```

Více v [API.md](API.md)

### Automatizace
Můžete vytvořit skripty pro:
- Automatické skenování pomocí cron/Task Scheduler
- Hromadné přiřazení metadat
- Export dat
- Backup databáze

---

## 🆘 Kde najít pomoc

- **Dokumentace**: [WEB_UI.md](WEB_UI.md)
- **API Reference**: [API.md](API.md)
- **Migrace**: [MIGRATION.md](MIGRATION.md)
- **GitHub Issues**: Otevřete issue pro bug report nebo feature request

---

**Užívejte Streamlet Connector! 🎬🍿**
