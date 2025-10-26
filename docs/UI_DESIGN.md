# Web UI - Vizuální průvodce

## 📸 Přehled stránek

### 1. Databáze (hlavní stránka)

```
┌──────────────────────────────────────────────────────────────┐
│ 🎬 Streamlet Connector          [ Databáze ] [ Nastavení ]   │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│ [ Hledat v databázi...        ] [ Vše ][ Filmy ][ Seriály ] │
│                                  [ Bez metadat ]              │
│                                                               │
│  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐      │
│  │ 🖼️  │  │ 🖼️  │  │ 🖼️  │  │ 🖼️  │  │ 🖼️  │  │ 🖼️  │      │
│  │     │  │     │  │     │  │     │  │     │  │     │      │
│  │Title│  │Title│  │Title│  │Title│  │Title│  │Title│      │
│  │⭐7.5│  │⭐8.1│  │⭐9.0│  │⭐6.8│  │⭐7.2│  │⭐8.5│      │
│  └─────┘  └─────┘  └─────┘  └─────┘  └─────┘  └─────┘      │
│                                                               │
│  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐      │
│  │ 🖼️  │  │ 🖼️  │  │ 🖼️  │  │ 🖼️  │  │ 🖼️  │  │ 🖼️  │      │
│  │     │  │     │  │     │  │     │  │     │  │     │      │
│  │Title│  │Title│  │Title│  │Title│  │Title│  │Title│      │
│  │⭐7.8│  │⭐8.9│  │⭐7.1│  │⭐9.2│  │⭐6.5│  │⭐8.0│      │
│  └─────┘  └─────┘  └─────┘  └─────┘  └─────┘  └─────┘      │
└──────────────────────────────────────────────────────────────┘
```

**Popis:**
- **Header**: Logo + navigace (Databáze aktivní = modrá)
- **Search bar**: Vyhledávací pole + filtry
- **Grid**: Karty médií (6 sloupců na desktopu)
- **Karty**: Poster + název + hodnocení

### 2. Karta média (normální)

```
┌───────────────┐
│   [POSTER]    │  Standard look
│               │  - Černé pozadí
│   200x300px   │  - Při hoveru: posunutí nahoru + modrý stín
│               │  - Kurzor: pointer
│───────────────│
│ Title of Film │  Název (bold, bílý)
│ 2024  ⭐ 8.5  │  Rok + hodnocení (zlatá hvězda)
└───────────────┘
```

### 3. Karta bez metadat

```
┌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┐
│ [ Bez dat ]   │  Badge (červený, pravý horní roh)
│   [POSTER]    │  Přerušovaný červený rámeček
│   nebo  ?     │  Placeholder pokud není poster
│   200x300px   │
│╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌│
│ video_file.mp4│  Název souboru
│ movie         │  Typ
└╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┘
```

### 4. Detail média (modal)

```
┌────────────────────────────────────────────────────────┐
│                                               [   X   ]│
│  ┌─────────┐  ╔═══════════════════════════════════╗  │
│  │ POSTER  │  ║ The Matrix                        ║  │
│  │         │  ║ 1999 • 136 min • ⭐ 8.7          ║  │
│  │ 200x300 │  ║                                   ║  │
│  │         │  ║ A computer hacker learns from...  ║  │
│  └─────────┘  ║                                   ║  │
│               ║ [  ▶ Přehrát  ] [ ⬇ Stáhnout  ]  ║  │
│               ╚═══════════════════════════════════╝  │
│                                                        │
│  [ VIDEO PLAYER - pokud se přehrává ]                 │
│                                                        │
│  Soubor: \\server\Movies\The.Matrix.1999.mkv          │
└────────────────────────────────────────────────────────┘
```

**Prvky:**
- X button (pravý horní roh, šedý)
- Poster (200x300px, zaoblené rohy)
- Název (velký, modrý)
- Meta info (rok, délka, hodnocení)
- Popis filmu
- Tlačítka (modrá, zaoblená)
- Video player (pokud se přehrává)
- Cesta k souboru (malé písmo, šedé)

### 5. Detail bez metadat (modal)

```
┌────────────────────────────────────────────────────────┐
│                                               [   X   ]│
│                                                        │
│                      ❓                                │
│                                                        │
│          Položka bez metadat                          │
│                                                        │
│     \\server\Movies\unknown_movie.mkv                 │
│                                                        │
│     [ 🔍 Přiřadit metadata z TMDB ]                   │
│                                                        │
└────────────────────────────────────────────────────────┘
```

### 6. TMDB Search Modal

```
┌────────────────────────────────────────────────────────┐
│                                               [   X   ]│
│  Přiřadit metadata z TMDB                             │
│                                                        │
│  Soubor: unknown_movie.mkv                            │
│                                                        │
│  [ Hledat film/seriál...    ] [ Film ][ Seriál ]     │
│                                [ Hledat ]             │
│                                                        │
│  ┌──────────────────────────────────────────────────┐ │
│  │ ┌────┐  The Matrix (1999) ⭐ 8.7               │ │
│  │ │ 📷 │  A computer hacker learns...             │ │
│  │ └────┘                                           │ │
│  ├──────────────────────────────────────────────────┤ │
│  │ ┌────┐  The Matrix Reloaded (2003) ⭐ 7.2       │ │
│  │ │ 📷 │  Six months after...                     │ │
│  │ └────┘                                           │ │
│  ├──────────────────────────────────────────────────┤ │
│  │ ┌────┐  The Matrix Revolutions (2003) ⭐ 6.8    │ │
│  │ │ 📷 │  The human city...                       │ │
│  │ └────┘                                           │ │
│  └──────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────┘
```

**Prvky:**
- Název souboru (odkaz na původní položku)
- Typ selector (Film/Seriál), aktivní = modrý
- Vyhledávací pole + tlačítko
- Seznam výsledků (scrollovatelný, max 400px)
- Každý výsledek: mini poster + název + rok + hodnocení + popis

### 7. Nastavení

```
┌──────────────────────────────────────────────────────────────┐
│ 🎬 Streamlet Connector          [ Databáze ] [ Nastavení ]   │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ TMDB Nastavení                                          │ │
│  │                                                         │ │
│  │ API Klíč                                                │ │
│  │ [ _____________________________ ]                       │ │
│  │                                                         │ │
│  │ Jazyk                                                   │ │
│  │ [ Čeština                ▼ ]                           │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ Složky ke skenování                                     │ │
│  │                                                         │ │
│  │ Přidat složku                                           │ │
│  │ [ /mnt/movies___________  ] [ Přidat ]                 │ │
│  │                                                         │ │
│  │ ┌─────────────────────────────────────────────────────┐│ │
│  │ │ \\server\Movies              [ Odebrat ]           ││ │
│  │ ├─────────────────────────────────────────────────────┤│ │
│  │ │ /mnt/tv_shows                [ Odebrat ]           ││ │
│  │ └─────────────────────────────────────────────────────┘│ │
│  │                                                         │ │
│  │ [ 🔍 Spustit skenování ]                               │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                               │
│  [ 💾 Uložit nastavení ]                                     │
└──────────────────────────────────────────────────────────────┘
```

**Sekce:**
1. TMDB Nastavení (API klíč + jazyk dropdown)
2. Složky ke skenování (input + seznam + skenování button)
3. Uložit nastavení button (velký, modrý)

---

## 🎨 Barevná paleta

### Tmavý theme
```
Pozadí:         #0f0f0f  ████████  (téměř černá)
Karty:          #1a1a1a  ████████  (tmavě šedá)
Hovery:         #2a2a2a  ████████  (střední šedá)
Text:           #e0e0e0  ████████  (světle šedá)
Disabled:       #999999  ████████  (šedá)
```

### Barevné akcenty
```
Primární:       #9DD8FF  ████████  (světle modrá)
Hover:          #7ac5f5  ████████  (modrá)
Varování:       #ff6b6b  ████████  (červená)
Úspěch:         #4caf50  ████████  (zelená)
Zlatá:          #ffd700  ████████  (zlatá - hodnocení)
```

---

## 📐 Rozměry

### Karty
- **Poster**: 200px × 300px
- **Gap**: 20px mezi kartami
- **Radius**: 8px zaoblené rohy
- **Padding**: 15px uvnitř card-info

### Modal
- **Max width**: 900px
- **Padding**: 30px
- **Radius**: 12px
- **Max height**: 90vh (scrollovatelný)

### Fonts
- **Heading**: 24-32px
- **Body**: 14-16px
- **Small**: 12-13px
- **Family**: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto

### Spacing
- **Container padding**: 30px
- **Section margin**: 20px mezi sekcemi
- **Form gap**: 20px mezi prvky

---

## 🎭 Stavy

### Karty
- **Default**: Stín 0
- **Hover**: Transform translateY(-5px) + stín rgba(157,216,255,0.3)
- **Bez metadat**: Border 2px dashed #ff6b6b

### Tlačítka
- **Default**: Background #9DD8FF
- **Hover**: Background #7ac5f5
- **Secondary**: Background #2a2a2a
- **Secondary hover**: Background #3a3a3a

### Inputy
- **Default**: Border #333
- **Focus**: Border #9DD8FF, outline none

### Filtry
- **Default**: Background #2a2a2a
- **Active**: Background #9DD8FF, color #000
- **Hover (inactive)**: Background #3a3a3a

---

## 📱 Responzivní breakpoints

### Desktop (default)
- Grid: `repeat(auto-fill, minmax(200px, 1fr))`
- Modal: 900px max-width
- Container: 1600px max-width

### Mobile (< 768px)
```css
.modal-header { flex-direction: column }
.modal-poster { width: 100%, height: auto }
.search-bar { flex-direction: column }
.search-input { min-width: 100% }
```

---

## ⚡ Animace

### Transitions
- Karty: `transform 0.3s, box-shadow 0.3s`
- Tlačítka: `background 0.3s`
- Inputy: `border-color 0.3s`
- Nav: `all 0.3s`

### Hover efekty
- Karty: Pohyb nahoru + modrý stín
- Tlačítka: Změna odstínu modré
- Close button: Změna barvy #999 → #fff

---

## 🔤 Ikony & Emoji

### Použité emoji
- 🎬 Logo
- 📂 Prázdný stav databáze
- ❓ Položka bez metadat
- 🔍 Vyhledávání / Skenování
- ⚙️ Nastavení
- ▶️ Přehrát
- ⬇️ Stáhnout
- ⭐ Hodnocení
- 💾 Uložit
- ✓ Úspěch
- ✗ Chyba

### Badge
- "Bez dat" - červený, pravý horní roh
- Padding: 5px 10px
- Border-radius: 5px
- Font-size: 12px

---

**Tip**: Pro přesné barvy otevřete DevTools a zkopírujte CSS proměnné!
