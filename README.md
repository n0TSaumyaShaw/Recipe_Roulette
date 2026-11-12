<p align="center">
  <img src="assets/images/icons/logo-512.png" alt="Recipe Roulette logo" width="120" />
</p>

# Recipe Roulette: Shinchan Edition 📱🍜

An interactive, comic-styled survival recipe generator built as Shinchan's Phone OS, turning leftover kitchen ingredients into delicious local and global meals with authentic Shinchan humor!

---

## 🏆 Hackathon Context

- **Event:** ROGUEHACK 1.0
- **Organized By:** Hack The Box SRMIST Student Chapter
- **Theme:** Shinchan (Crayon Shin-chan / クレヨンしんちゃん)
- **Problem Track:** Recipe Roulette — Empty Fridge Survival Guide

---

## 🌟 Key Features

1. **Shinchan's Phone OS UI**:
   - Realistic smartphone frame featuring a status notch with clock, Wi-Fi, battery, and **Mom's live Anger Meter**.
   - **Phone Home Screen** with an interactive 10-App Grid:
     - 🧊 **Fridge** (Recipe Roulette with reel spinner and smart ingredient chips)
     - 👩 **Mom** (English chat intro replay)
     - ⚡ **Action Kamen TV** (Interactive Action Beam blaster)
     - 🍫 **Chocobi Delivery** (Order Chocobi with live delivery tracker)
     - 🐶 **Shiro's Gallery** (Interactive pet-the-dog simulator)
     - 📝 **Shinchan's Notes** (Handwritten notepad with scribble generator)
     - 📖 **Cookbook** (Session tracker recording all cooked recipes and Mummy's verdicts)
     - ☀️ **Weather** ("*90% chance of Mom yelling, 100% chance of chocobi*")
     - 👥 **Contacts** (Nohara family and Kasukabe Defense Force phonebook)
     - ⚙️ **Settings** (Audio toggle, Anger meter reset, developer credits)
   - Bottom navigation bar: `[Home]`, `[Fridge]`, `[Cookbook]`, `[Notes]`.

2. **Smart Recipe Roulette & Engine**:
   - **50 Handcrafted Local Recipes** in `data/recipes.json` (including 15 Indian & Desi hostel survival staples like *Masala Omelette*, *Anda Bhurji*, *Dahi Tadka*, and *Paneer Tikka*).
   - **World Kitchen 🌍 Mode**: Hybrid integration with TheMealDB API (`filter.php` multi-ingredient frequency ranking + `lookup.php` full dish details) with in-memory caching and offline fallback.
   - **Tappable Ingredient Chips & Custom Additions**: Quickly pick items from your fridge or type custom ingredients.
   - **Hated Ingredient Alarm**: Selecting green pepper (*piman*) or eggplant (*brinjal*) triggers Shinchan's dramatic tantrum, a red screen flash, and increases Mom's Anger Meter by +35%.
   - **Mom's 100% Rage Event**: Intense screen shaking with the iconic *"SHIN-CHAN!!!!!"* modal when Mom's patience runs out.
   - **Battery Drain**: Realistic battery drops 1% per spin from 85%, alerting *"Mom, please bring the charger!"* at 1%.
   - **Periodic Notifications**: Slide-in notification banners every ~15 seconds with quips from Hiroshi, Shiro, Kazama, Nanako-san, and Action Kamen.
   - **Web Audio Sound Effects**: Zero external audio files; all beeps, boops, fanfares, and alarm sounds generated via the Web Audio API with synchronized mute controls in both the header and Fridge screen.

---

## 🛠️ Tech Stack

- **Frontend:** Semantic HTML5, Modern CSS3 (CSS Grid, Flexbox, custom comic keyframes, Google Fonts: *Bangers*, *Fredoka*, *Gochi Hand*)
- **Logic:** Vanilla ES6+ JavaScript (Zero external libraries or build step)
- **Audio:** Web Audio API (`AudioContext`, `OscillatorNode`, `GainNode`)
- **API:** TheMealDB API (Free World Kitchen integration)
- **Deployment:** Vercel (Zero-config static hosting)

---

## 📂 Project Structure

```text
yeahHTBHackathon/
├── index.html                       <- Main HTML document (Vercel entrypoint)
├── vercel.json                      <- Vercel deployment configuration
├── .vercelignore                    <- Deployment exclusions
├── .gitignore                       <- Git ignore rules
├── README.md                        <- Project documentation
├── css/
│   └── style.css                    <- Complete comic phone OS styling & animations
├── js/
│   └── script.js                    <- Core app logic, audio synthesis, and OS state
├── data/
│   └── recipes.json                 <- 50 curated local recipes
├── assets/
│   └── images/
│       └── avatars/                 <- Character profile photos (misae-pfp.webp, shinchan-pfp.jpg)
└── tests/
    └── test_app.py                  <- Automated end-to-end browser verification suite
```

---

## 💻 How to Run Locally

Because the application fetches `data/recipes.json` asynchronously, run it using a local HTTP server:

```bash
# Clone the repository
git clone https://github.com/n0TSaumyaShaw/Recipe_Roulette.git
cd Recipe_Roulette

# Start a local static server (Python 3)
python -m http.server 8080
```

Now open your browser and navigate to:
**`http://localhost:8080/`**

---

## 📸 Screenshots

| Phone Home Screen | Recipe Roulette (Fridge) |
|:---:|:---:|
| ![Phone Home Screen](docs/screenshots/home.png) | ![Recipe Roulette Fridge](docs/screenshots/fridge.png) |

| World Kitchen Mode | Mom's 100% Rage Modal |
|:---:|:---:|
| ![World Kitchen Mode](docs/screenshots/world.png) | ![Mom's 100% Rage Modal](docs/screenshots/rage.png) |

| Shiro's Pet Care & Gallery | Kasukabe Contacts |
|:---:|:---:|
| ![Shiro Pet Care and Gallery](docs/screenshots/shiro.png) | ![Kasukabe Contacts Directory](docs/screenshots/contacts.png) |

---

## 📜 Credits & Disclaimer

- **Recipe Data:** [TheMealDB](https://www.themealdb.com/) for public World Kitchen meal data and ingredients.
- **Fonts:** [Google Fonts](https://fonts.google.com/) (*Bangers*, *Fredoka*, *Gochi Hand*, *Comic Neue*).
- **Disclaimer:** This is an unofficial, non-commercial fan-made project created solely for the **ROGUEHACK 1.0** hackathon. *Crayon Shin-chan* and all related characters and trademarks are the property of Yoshito Usui, Futabasha, Shin-Ei Animation, and TV Asahi. No copyright infringement is intended.

---

## 👤 Author

- **Name:** Saumya Shaw
- **Hackathon Team:** Exodus (Members: Only me)
- **Institution:** SRM Institute of Science and Technology (SRMIST)
- **GitHub:** [@n0TSaumyaShaw](https://github.com/n0TSaumyaShaw)
