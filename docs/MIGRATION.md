# Přechod na Web UI

## Co se změnilo?

Streamlet Connector nyní používá **webové uživatelské rozhraní** místo Python Tkinter GUI. Veškeré ovládání probíhá v prohlížeči.

## Výhody nového UI

✅ **Přístup odkudkoliv** - Otevřete v prohlížeči z jakéhokoliv zařízení v síti  
✅ **Responzivní design** - Funguje na desktopu i mobilu  
✅ **Přehrávání videa** - Přehrávejte filmy přímo v prohlížeči  
✅ **Lepší UX** - Modernější a intuitivnější rozhraní  
✅ **Rychlejší** - Žádné zamrzání GUI, asynchronní operace  
✅ **Snadnější vývoj** - HTML/CSS/JS místo Tkinter  

## Migrace

### Krok 1: Aktualizace
Stáhněte nejnovější verzi z repozitáře.

### Krok 2: Spuštění
```bash
python run_api.py
```

### Krok 3: Otevření v prohlížeči
```
http://localhost:5000/ui
```

### Vaše data jsou zachována!
- Databáze médií: `data/media_db.json` ✅
- Obrázky: `data/images/` ✅
- Konfigurace: `config/config.json` ✅

Vše funguje stejně, jen v prohlížeči!

## Nové funkce

### 1. Přiřazení metadat
Nyní můžete snadno přiřadit metadata položkám bez dat:
1. Filtrujte "Bez metadat"
2. Klikněte na položku
3. Vyhledejte v TMDB
4. Vyberte správný výsledek
5. Hotovo!

### 2. Přehrávání v prohlížeči
Klikněte na film → "Přehrát" → Video se otevře přímo v prohlížeči

### 3. Lepší vyhledávání
Rychlé vyhledávání v názvech i cestách souborů

### 4. Vizuální označení
Položky bez metadat mají červený přerušovaný rámeček

## Staré Tkinter UI

Pokud potřebujete staré Tkinter UI, stále můžete použít:
```bash
python main.py
```

Ale doporučujeme přejít na Web UI, které nabízí více funkcí.

## Podpora

Máte problémy? Otevřete issue na GitHubu nebo se podívejte do [WEB_UI.md](WEB_UI.md) pro podrobnou dokumentaci.

## FAQ

**Q: Musím přenést data?**  
A: Ne, všechna data se automaticky načtou z `data/media_db.json`

**Q: Funguje na telefonu?**  
A: Ano! UI je responzivní a funguje i na mobilních zařízeních

**Q: Můžu to otevřít z jiného počítače?**  
A: Ano, server běží na `0.0.0.0`, takže je dostupný ze sítě. Použijte IP adresu serveru, např. `http://192.168.0.199:5000/ui`

**Q: Je to bezpečné?**  
A: Pro lokální síť ano. Pro internet doporučujeme použít reverse proxy s HTTPS a autentizací.

**Q: Kde jsou API endpointy?**  
A: Všechny endpointy najdete v [API.md](API.md), web UI používá tyto nové endpointy:
- `/api/items` - Všechny položky
- `/api/search` - Vyhledávání TMDB
- `/api/assign-metadata` - Přiřazení metadat
- `/api/settings` - Nastavení
- `/api/scan` - Skenování
