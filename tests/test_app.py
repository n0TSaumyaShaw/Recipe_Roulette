import asyncio
import websockets
import json
import urllib.request
import subprocess
import time
import os
import base64

CHROME_PATH = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
PORT = 9455

# Contrast calculation helpers
def parse_rgba(color_str):
    if not color_str:
        return (0, 0, 0, 1.0)
    color_str = color_str.strip().lower()
    if color_str.startswith('rgb'):
        nums = [float(x.strip()) for x in color_str.replace('rgba(', '').replace('rgb(', '').replace(')', '').split(',')]
        r, g, b = nums[0], nums[1], nums[2]
        a = nums[3] if len(nums) > 3 else 1.0
        return (r, g, b, a)
    return (0, 0, 0, 1.0)

def srgb_to_luminance(r, g, b):
    def channel_l(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * channel_l(r) + 0.7152 * channel_l(g) + 0.0722 * channel_l(b)

def calc_contrast_ratio(rgb1, rgb2):
    l1 = srgb_to_luminance(rgb1[0], rgb1[1], rgb1[2])
    l2 = srgb_to_luminance(rgb2[0], rgb2[1], rgb2[2])
    bright = max(l1, l2)
    dark = min(l1, l2)
    return (bright + 0.05) / (dark + 0.05)

async def run_comprehensive_test():
    os.makedirs('screenshots', exist_ok=True)
    os.makedirs('tests', exist_ok=True)

    cmd = [
        CHROME_PATH,
        '--headless=new',
        '--no-sandbox',
        '--disable-gpu',
        f'--remote-debugging-port={PORT}',
        r'--user-data-dir=C:\Users\Saumya\AppData\Local\Temp\chrome_app_full_test_9455',
        'http://localhost:8080/index.html'
    ]
    proc = subprocess.Popen(cmd)
    print("Launching headless Chrome...", flush=True)
    time.sleep(2)
    try:
        ws_url = None
        for attempt in range(10):
            try:
                req = urllib.request.urlopen(f'http://127.0.0.1:{PORT}/json', timeout=2)
                targets = json.loads(req.read().decode())
                page = next((t for t in targets if t.get('type') == 'page'), None)
                if page:
                    ws_url = page['webSocketDebuggerUrl']
                    break
            except Exception:
                time.sleep(0.5)

        if not ws_url:
            raise RuntimeError("Could not obtain webSocketDebuggerUrl from Chrome!")

        print(f"Connected to Chrome DevTools WebSocket: {ws_url}", flush=True)
        async with websockets.connect(ws_url, max_size=None) as ws:
            msg_id = 0
            console_errors = []
            network_errors = []

            async def send(method, params=None):
                nonlocal msg_id
                msg_id += 1
                await ws.send(json.dumps({'id': msg_id, 'method': method, 'params': params or {}}))
                while True:
                    resp = json.loads(await ws.recv())
                    if resp.get('method') == 'Runtime.consoleAPICalled':
                        args = resp.get('params', {}).get('args', [])
                        text = ' '.join(str(a.get('value', '')) for a in args)
                        if resp.get('params', {}).get('type') == 'error':
                            console_errors.append(text)
                            print(f"[BROWSER ERROR] {text}")
                    elif resp.get('method') == 'Runtime.exceptionThrown':
                        details = resp.get('params', {}).get('exceptionDetails', {})
                        text = details.get('text', '') + ' ' + details.get('exception', {}).get('description', '')
                        console_errors.append(text)
                        print(f"[UNCAUGHT EXCEPTION] {text}")
                    elif resp.get('method') == 'Network.responseReceived':
                        params = resp.get('params', {})
                        response = params.get('response', {})
                        status = response.get('status', 200)
                        url = response.get('url', '')
                        if status >= 400 and not url.endswith('favicon.ico'):
                            network_errors.append(f"{status} on {url}")
                            print(f"[NETWORK ERROR] {status} on {url}")
                    elif resp.get('id') == msg_id:
                        return resp.get('result', {})

            await send('Runtime.enable')
            await send('Page.enable')
            await send('Network.enable')
            await send('Network.setCacheDisabled', {'cacheDisabled': True})

            # Wait for load
            await asyncio.sleep(1.5)

            # Check 0: Verify Favicon and Theme Color
            print("0. Verifying Favicon and Theme Color in <head> and root /favicon.ico...")
            fav_req = urllib.request.urlopen('http://localhost:8080/favicon.ico')
            assert fav_req.status == 200, f"Expected 200 on /favicon.ico, got {fav_req.status}"
            print("   ✓ Root /favicon.ico is accessible with HTTP 200")

            fav_check = await send('Runtime.evaluate', {
                'expression': """(() => {
                    const svg = document.querySelector('link[rel="icon"][type="image/svg+xml"]');
                    const png = document.querySelector('link[rel="icon"][sizes="32x32"]');
                    const ico = document.querySelector('link[rel="shortcut icon"]');
                    const apple = document.querySelector('link[rel="apple-touch-icon"]');
                    const theme = document.querySelector('meta[name="theme-color"]');
                    return {
                        svg: svg ? svg.getAttribute('href') : null,
                        png: png ? png.getAttribute('href') : null,
                        ico: ico ? ico.getAttribute('href') : null,
                        apple: apple ? apple.getAttribute('href') : null,
                        themeColor: theme ? theme.getAttribute('content') : null
                    };
                })()""",
                'returnByValue': True
            })
            fc = fav_check.get('result', {}).get('value', {})
            print("   Favicon Head Check:", fc)
            assert fc.get('svg') == 'assets/images/icons/favicon.svg', "favicon.svg missing or incorrect!"
            assert fc.get('png') == 'assets/images/icons/favicon-32.png', "favicon-32.png missing or incorrect!"
            assert fc.get('ico') == 'assets/images/icons/favicon.ico', "favicon.ico missing or incorrect!"
            assert fc.get('apple') == 'assets/images/icons/apple-touch-icon.png', "apple-touch-icon missing or incorrect!"
            assert fc.get('themeColor') == '#0f0f1a', "theme-color should be #0f0f1a!"

            # Check 1: Go to Home
            print("1. Navigating from chat intro to home screen...")
            nav_eval = await send('Runtime.evaluate', {'expression': '(() => { try { showPhoneScreen("home"); return { ok: true, active: document.getElementById("screen-home").classList.contains("active") }; } catch (e) { return { error: e.message, stack: e.stack }; } })()', 'returnByValue': True})
            print("   nav_eval:", nav_eval)
            await asyncio.sleep(0.3)

            # Check 1b: Verify 'Open the fridge' CTA on chat screen opens fridge screen directly
            print("1b. Testing 'Open the fridge' CTA on chat screen opens fridge screen directly...")
            await send('Runtime.evaluate', {'expression': 'showPhoneScreen("chat")'})
            await asyncio.sleep(0.2)
            await send('Runtime.evaluate', {'expression': 'document.getElementById("btn-open-fridge").click()'})
            await asyncio.sleep(0.3)
            opened_screen = await send('Runtime.evaluate', {'expression': 'currentPhoneScreen', 'returnByValue': True})
            print("   Current screen after 'Open the fridge':", opened_screen.get('result', {}).get('value'))
            assert opened_screen.get('result', {}).get('value') == 'fridge', "Expected fridge screen to open!"

            # Check 1c: Recipe of the day dynamically populated
            print("1c. Testing Recipe of the Day dynamically populated per day...")
            rotd_check = await send('Runtime.evaluate', {
                'expression': """(() => {
                    const name = document.getElementById('side-recipe-name').textContent.trim();
                    const meta = document.getElementById('side-recipe-meta').textContent.trim();
                    return { name, meta };
                })()""",
                'returnByValue': True
            })
            rc = rotd_check.get('result', {}).get('value', {})
            print("   Recipe of the Day:", rc)
            assert len(rc.get('name', '')) > 0, "Recipe of the day name should not be empty!"

            # Return to Home screen for app grid check
            await send('Runtime.evaluate', {'expression': 'showPhoneScreen("home")'})
            await asyncio.sleep(0.2)

            # Check 2: Verify 9 Apps in Grid and No Notch
            home_state = await send('Runtime.evaluate', {
                'expression': """(() => {
                    return {
                        active: document.getElementById('screen-home').classList.contains('active'),
                        appCount: document.querySelectorAll('.app-item').length,
                        notchPresent: document.querySelector('.phone-notch') !== null
                    };
                })()""",
                'returnByValue': True
            })
            val_home = home_state.get('result', {}).get('value', {})
            print("   Home State:", val_home)
            assert val_home.get('active') is True, "Home screen not active!"
            assert val_home.get('appCount') == 9, f"Expected exactly 9 apps, got {val_home.get('appCount')}!"
            assert val_home.get('notchPresent') is False, "Notch should be completely removed!"

            # Check 3: Test Navigation Across All 9 Phone Apps
            apps = ['fridge', 'chat', 'action-kamen', 'shiro', 'notes', 'cookbook', 'weather', 'contacts', 'settings']
            print(f"2. Testing navigation for all {len(apps)} apps (no Chocobi)...")
            for app in apps:
                await send('Runtime.evaluate', {'expression': f'showPhoneScreen("{app}")'})
                await asyncio.sleep(0.15)
                cur = await send('Runtime.evaluate', {'expression': 'currentPhoneScreen', 'returnByValue': True})
                assert cur.get('result', {}).get('value') == app, f"Failed navigating to app: {app}"
                print(f"   ✓ App [{app}] navigated successfully")

            # Check 3b: Test Contacts App PFPs and Pop-Down Notification Avatars
            print("2b. Testing Contacts PFPs and Notification Avatars...")
            await send('Runtime.evaluate', {'expression': 'showPhoneScreen("contacts")'})
            await asyncio.sleep(0.3)

            contact_pfps_check = await send('Runtime.evaluate', {
                'expression': """(() => {
                    const cards = Array.from(document.querySelectorAll('#contacts-list .contact-card'));
                    return cards.map(c => {
                        const caller = c.dataset.caller;
                        const img = c.querySelector('img.contact-pfp');
                        return {
                            caller,
                            hasImg: !!img,
                            src: img ? img.getAttribute('src') : null,
                            loaded: img ? (img.complete && img.naturalWidth > 0) : false
                        };
                    });
                })()""",
                'returnByValue': True
            })
            pfp_list = contact_pfps_check.get('result', {}).get('value', [])
            print("   Contact Cards PFPs:", pfp_list)
            assert len(pfp_list) == 6, f"Expected 6 contact cards, got {len(pfp_list)}"
            for c in pfp_list:
                assert c['hasImg'], f"Contact {c['caller']} is missing img.contact-pfp!"
                assert c['loaded'], f"Contact {c['caller']} image failed to load: {c['src']}"

            # Test Pop-Down Notification avatar rendering
            await send('Runtime.evaluate', {
                'expression': 'triggerPhoneNotification("DAD (HIROSHI)", "Mortgage reminder...", "👔", "assets/images/avatars/hiroshi-pfp.jpg")'
            })
            await asyncio.sleep(0.4)

            notif_avatar_check = await send('Runtime.evaluate', {
                'expression': """(() => {
                    const notif = document.getElementById('phone-notif');
                    const img = notif ? notif.querySelector('img.notif-img') : null;
                    return {
                        hasShow: notif ? notif.classList.contains('show') : false,
                        hasImg: !!img,
                        src: img ? img.getAttribute('src') : null,
                        loaded: img ? (img.complete && img.naturalWidth > 0) : false
                    };
                })()""",
                'returnByValue': True
            })
            nac = notif_avatar_check.get('result', {}).get('value', {})
            print("   Notification Pop-Down Avatar Check:", nac)
            assert nac.get('hasShow') is True, "Notification banner did not get .show class!"
            assert nac.get('hasImg') is True, "Notification banner missing img.notif-img!"
            assert nac.get('loaded') is True, f"Notification banner image failed to load: {nac.get('src')}"

            # Check 4: Test Sound FX in Settings App
            print("3. Testing Sound FX control via Settings toggle only...")
            await send('Runtime.evaluate', {'expression': 'showPhoneScreen("settings")'})
            await asyncio.sleep(0.2)
            # Verify soundEnabled is initially true
            s_init = await send('Runtime.evaluate', {'expression': 'soundEnabled', 'returnByValue': True})
            assert s_init.get('result', {}).get('value') is True, "soundEnabled should be true by default"

            # Toggle setting-sound-fx off
            await send('Runtime.evaluate', {
                'expression': """(() => {
                    const toggle = document.getElementById('setting-sound-fx');
                    toggle.checked = false;
                    toggle.dispatchEvent(new Event('change'));
                })()"""
            })
            s_off = await send('Runtime.evaluate', {'expression': 'soundEnabled', 'returnByValue': True})
            assert s_off.get('result', {}).get('value') is False, "soundEnabled did not mute via Settings!"
            print("   ✓ Sound muted successfully via Settings toggle")

            # Toggle setting-sound-fx back on
            await send('Runtime.evaluate', {
                'expression': """(() => {
                    const toggle = document.getElementById('setting-sound-fx');
                    toggle.checked = true;
                    toggle.dispatchEvent(new Event('change'));
                })()"""
            })
            s_on = await send('Runtime.evaluate', {'expression': 'soundEnabled', 'returnByValue': True})
            assert s_on.get('result', {}).get('value') is True, "soundEnabled did not unmute via Settings!"
            print("   ✓ Sound unmuted successfully via Settings toggle")

            # Check 5: Test Notes App input, character counter, local storage & delete
            print("4. Testing Notes App interactive input, character counter, and persistence...")
            await send('Runtime.evaluate', {'expression': 'showPhoneScreen("notes")'})
            await asyncio.sleep(0.2)

            # Type a secret note and verify counter
            await send('Runtime.evaluate', {
                'expression': """(() => {
                    const input = document.getElementById('note-input');
                    input.value = "Rule 6: Mom hides her emergency choco biscuits behind the rice jar!";
                    input.dispatchEvent(new Event('input'));
                })()"""
            })
            counter_val = await send('Runtime.evaluate', {
                'expression': 'document.getElementById("note-char-count").textContent',
                'returnByValue': True
            })
            print(f"   Char counter: {counter_val.get('result', {}).get('value')}")
            assert counter_val.get('result', {}).get('value') == "67/200", "Char counter mismatch!"

            # Click Add Note button
            await send('Runtime.evaluate', {'expression': 'document.getElementById("btn-add-note").click()'})
            await asyncio.sleep(0.2)

            # Check DOM for prepended user rule
            note_check = await send('Runtime.evaluate', {
                'expression': """(() => {
                    const userRule = document.querySelector('.notepad-list li.user-rule .note-text');
                    const rawStorage = localStorage.getItem('recipeRoulette.notes');
                    return {
                        domText: userRule ? userRule.textContent : null,
                        storage: JSON.parse(rawStorage || '[]')
                    };
                })()""",
                'returnByValue': True
            })
            n_res = note_check.get('result', {}).get('value', {})
            print("   Note Check:", n_res)
            assert n_res.get('domText') == "Rule 6: Mom hides her emergency choco biscuits behind the rice jar!", "DOM note text mismatch!"
            assert len(n_res.get('storage', [])) == 1, "LocalStorage notes count should be 1!"

            # Test note deletion
            await send('Runtime.evaluate', {
                'expression': 'document.querySelector(".notepad-list li.user-rule .btn-delete-note").click()'
            })
            await asyncio.sleep(0.2)
            del_check = await send('Runtime.evaluate', {
                'expression': """(() => {
                    const userRules = document.querySelectorAll('.notepad-list li.user-rule');
                    const rawStorage = localStorage.getItem('recipeRoulette.notes');
                    return {
                        domCount: userRules.length,
                        storageCount: JSON.parse(rawStorage || '[]').length
                    };
                })()""",
                'returnByValue': True
            })
            d_res = del_check.get('result', {}).get('value', {})
            assert d_res.get('domCount') == 0 and d_res.get('storageCount') == 0, "Note deletion failed!"
            print("   ✓ User note successfully added, persisted, and deleted")

            # Check 5b: Test Shiro Pet Care System
            print("4b. Testing Shiro Pet Care System (petting, feeding, moods, synth audio)...")
            await send('Runtime.evaluate', {'expression': 'showPhoneScreen("shiro")'})
            await asyncio.sleep(0.3)

            # Test Mood Evaluation across all 4 criteria
            mood_eval_check = await send('Runtime.evaluate', {
                'expression': """(() => {
                    return {
                        hungry: getShiroMood(20, 80, 12),     // hunger < 30 -> hungry
                        sleepyHour: getShiroMood(80, 80, 23), // 11pm -> sleepy
                        sleepyEnergy: getShiroMood(80, 20, 12), // energy < 25 -> sleepy
                        playful: getShiroMood(80, 70, 15),    // 3pm & energy > 50 -> playful
                        happy: getShiroMood(80, 70, 11)       // 11am -> happy
                    };
                })()""",
                'returnByValue': True
            })
            mc = mood_eval_check.get('result', {}).get('value', {})
            print("   Shiro Mood Evaluation Check:", mc)
            assert mc.get('hungry') == 'hungry', "Mood hunger < 30 failed!"
            assert mc.get('sleepyHour') == 'sleepy', "Mood 11pm sleepy failed!"
            assert mc.get('sleepyEnergy') == 'sleepy', "Mood low energy sleepy failed!"
            assert mc.get('playful') == 'playful', "Mood 3pm playful failed!"
            assert mc.get('happy') == 'happy', "Mood happy default failed!"

            # Test Petting each part: head, ears, belly, tail
            pet_check = await send('Runtime.evaluate', {
                'expression': """(() => {
                    const parts = ['head', 'ears', 'belly', 'tail'];
                    const initialPets = getShiroState().pets;
                    parts.forEach(p => {
                        const el = document.getElementById('shiro-' + p);
                        if (el) el.dispatchEvent(new MouseEvent('click', { bubbles: true }));
                    });
                    const stateAfter = getShiroState();
                    const speechText = document.getElementById('shiro-speech').textContent;
                    return {
                        petsGained: stateAfter.pets - initialPets,
                        speechText,
                        dataMood: document.getElementById('shiro-pet-svg').getAttribute('data-mood')
                    };
                })()""",
                'returnByValue': True
            })
            pc = pet_check.get('result', {}).get('value', {})
            print("   Shiro Pet Parts Check:", pc)
            assert pc.get('petsGained') == 4, f"Expected 4 pets recorded, got {pc.get('petsGained')}"
            assert len(pc.get('speechText', '')) > 5, "Shiro speech text should not be empty!"

            # Test Feeding Shiro
            feed_check = await send('Runtime.evaluate', {
                'expression': """(() => {
                    const hungerBefore = getShiroState().hunger;
                    document.getElementById('btn-feed-shiro').click();
                    const hungerAfter = getShiroState().hunger;
                    const speech = document.getElementById('shiro-speech').textContent;
                    return {
                        hungerBefore,
                        hungerAfter,
                        speech
                    };
                })()""",
                'returnByValue': True
            })
            fc = feed_check.get('result', {}).get('value', {})
            print("   Shiro Feeding Check:", fc)
            assert len(fc.get('speech', '')) > 0, "Feeding dialogue should display!"

            # Test Shiro Storage Persistence
            shiro_store_check = await send('Runtime.evaluate', {
                'expression': """(() => {
                    const raw = localStorage.getItem('recipeRoulette.shiro');
                    const parsed = JSON.parse(raw || '{}');
                    return {
                        exists: !!raw,
                        hasHunger: typeof parsed.hunger === 'number',
                        hasHappiness: typeof parsed.happiness === 'number',
                        hasEnergy: typeof parsed.energy === 'number',
                        pets: parsed.pets
                    };
                })()""",
                'returnByValue': True
            })
            ssc = shiro_store_check.get('result', {}).get('value', {})
            print("   Shiro Storage Check:", ssc)
            assert ssc.get('exists') is True and ssc.get('pets') >= 4, "Shiro state not persisted in localStorage!"

            # Check 6: Test Recipe Roulette Cooking in Fridge
            print("5. Testing Recipe Roulette in Fridge Screen...")
            await send('Runtime.evaluate', {'expression': 'showPhoneScreen("fridge")'})
            await asyncio.sleep(0.3)

            # Check recipes loaded from data/recipes.json
            recipe_count = await send('Runtime.evaluate', {'expression': 'allRecipes.length', 'returnByValue': True})
            cnt = recipe_count.get('result', {}).get('value', 0)
            print(f"   Loaded recipes count: {cnt}")
            assert cnt >= 50, f"Expected 50 recipes, got {cnt}!"

            # Select eggs, onion, bread and click Cook
            await send('Runtime.evaluate', {
                'expression': '(() => { clearSelections(); [...document.querySelectorAll(".chip")].filter(c => ["eggs", "onion", "bread"].includes(c.dataset.name)).forEach(c => c.click()); })()'
            })
            bat_before = await send('Runtime.evaluate', {'expression': 'batteryPercent', 'returnByValue': True})
            anger_before = await send('Runtime.evaluate', {'expression': 'momAnger', 'returnByValue': True})

            await send('Runtime.evaluate', {'expression': 'document.getElementById("btn-cook").click()'})
            await asyncio.sleep(2.5)

            bat_after = await send('Runtime.evaluate', {'expression': 'batteryPercent', 'returnByValue': True})
            anger_after = await send('Runtime.evaluate', {'expression': 'momAnger', 'returnByValue': True})
            cooked_title = await send('Runtime.evaluate', {'expression': 'document.getElementById("card-recipe-title").textContent.trim()', 'returnByValue': True})

            print(f"   Cooked Dish: '{cooked_title.get('result', {}).get('value')}'")
            print(f"   Battery: {bat_before.get('result', {}).get('value')}% -> {bat_after.get('result', {}).get('value')}%")
            print(f"   Anger: {anger_before.get('result', {}).get('value')}% -> {anger_after.get('result', {}).get('value')}%")
            assert bat_after.get('result', {}).get('value') == bat_before.get('result', {}).get('value') - 1, "Battery drain failed!"
            assert anger_after.get('result', {}).get('value') > anger_before.get('result', {}).get('value'), "Anger did not increase!"

            # Verify action buttons layout in .card-actions
            btn_layout = await send('Runtime.evaluate', {
                'expression': """(() => {
                    const spin = document.getElementById('btn-spin-again');
                    const copy = document.getElementById('btn-copy-recipe');
                    const edit = document.getElementById('btn-change-ingredients');
                    const spinRect = spin.getBoundingClientRect();
                    const copyRect = copy.getBoundingClientRect();
                    const editRect = edit.getBoundingClientRect();
                    return {
                        spinRow1: spinRect.top < copyRect.top,
                        copyAndEditSameRow: Math.abs(copyRect.top - editRect.top) < 4,
                        spinFullWidth: spinRect.width > copyRect.width * 1.5
                    };
                })()""",
                'returnByValue': True
            })
            bl = btn_layout.get('result', {}).get('value', {})
            print("   Action Buttons Layout:", bl)
            assert bl.get('spinRow1') and bl.get('copyAndEditSameRow') and bl.get('spinFullWidth'), "Card action buttons layout incorrect!"

            # -----------------------------------------------------------------
            # PERSISTENCE & STORAGE MODULE VERIFICATION (recipeRoulette.v1)
            # -----------------------------------------------------------------
            print("\n5b. Testing Persistence, Favorites, Cookbook Tabs, and Storage Module...")

            # Cook 2 more recipes (total 3 cooked)
            await send('Runtime.evaluate', {
                'expression': '(() => { clearSelections(); [...document.querySelectorAll(".chip")].filter(c => ["potato", "onion", "butter"].includes(c.dataset.name)).forEach(c => c.click()); document.getElementById("btn-cook").click(); })()'
            })
            await asyncio.sleep(2.5)

            await send('Runtime.evaluate', {
                'expression': '(() => { clearSelections(); [...document.querySelectorAll(".chip")].filter(c => ["tomato", "cheese", "bread"].includes(c.dataset.name)).forEach(c => c.click()); document.getElementById("btn-cook").click(); })()'
            })
            await asyncio.sleep(2.5)

            # Verify localStorage.getItem('recipeRoulette.v1')
            storage_check = await send('Runtime.evaluate', {
                'expression': """(() => {
                    const raw = localStorage.getItem('recipeRoulette.v1');
                    const state = raw ? JSON.parse(raw) : null;
                    return {
                        exists: !!state,
                        historyCount: state ? (state.history || []).length : 0,
                        cookedStat: state && state.stats ? state.stats.cooked : 0,
                        lastIngredients: state ? state.lastIngredients : [],
                        prefs: state ? state.prefs : null
                    };
                })()""",
                'returnByValue': True
            })
            sc = storage_check.get('result', {}).get('value', {})
            print("   Storage after 3 cooked recipes:", sc)
            assert sc.get('exists') is True, "Storage key 'recipeRoulette.v1' not found!"
            assert sc.get('historyCount') >= 3, f"Expected at least 3 history items, got {sc.get('historyCount')}"
            assert sc.get('cookedStat') >= 3, f"Expected cooked stat >= 3, got {sc.get('cookedStat')}"

            # Test Favoriting current recipe
            fav_btn_state = await send('Runtime.evaluate', {
                'expression': """(() => {
                    const btn = document.getElementById('btn-favorite-recipe');
                    btn.click();
                    const state = JSON.parse(localStorage.getItem('recipeRoulette.v1') || '{}');
                    return {
                        isFavoritedClass: btn.classList.contains('favorited'),
                        favoritesCount: (state.favorites || []).length,
                        favoriteDish: (state.favorites || [])[0] ? state.favorites[0].name : null
                    };
                })()""",
                'returnByValue': True
            })
            fbs = fav_btn_state.get('result', {}).get('value', {})
            print("   Favorite Button State:", fbs)
            assert fbs.get('isFavoritedClass') is True, "Favorite button should have 'favorited' class!"
            assert fbs.get('favoritesCount') >= 1, "Favorites array in storage should have >= 1 item!"

            # Test Cookbook Screen and Tabs
            await send('Runtime.evaluate', {'expression': 'showPhoneScreen("cookbook")'})
            await asyncio.sleep(0.3)

            cb_check = await send('Runtime.evaluate', {
                'expression': """(() => {
                    const histCount = document.querySelectorAll('#cookbook-list .cooked-dish-card').length;
                    const histBadge = document.getElementById('cookbook-history-count').textContent.trim();
                    const favBadge = document.getElementById('cookbook-favorites-count').textContent.trim();
                    
                    // Switch to favorites tab
                    document.getElementById('tab-cookbook-favorites').click();
                    const favCount = document.querySelectorAll('#cookbook-list .cooked-dish-card').length;

                    // Switch back to history tab
                    document.getElementById('tab-cookbook-history').click();
                    const histCountBack = document.querySelectorAll('#cookbook-list .cooked-dish-card').length;

                    return {
                        histCount,
                        histBadge,
                        favBadge,
                        favCount,
                        histCountBack
                    };
                })()""",
                'returnByValue': True
            })
            cbc = cb_check.get('result', {}).get('value', {})
            print("   Cookbook Tabs Check:", cbc)
            assert cbc.get('histCount') >= 3, f"Cookbook history should show >= 3 cards, got {cbc.get('histCount')}"
            assert cbc.get('favCount') >= 1, f"Cookbook favorites should show >= 1 card, got {cbc.get('favCount')}"

            # Test Resume Last Ingredients button on Fridge Screen
            await send('Runtime.evaluate', {'expression': 'showPhoneScreen("fridge")'})
            await asyncio.sleep(0.2)

            resume_check = await send('Runtime.evaluate', {
                'expression': """(() => {
                    const btnResume = document.getElementById('btn-resume-ingredients');
                    const initialDisplay = window.getComputedStyle(btnResume).display;
                    clearSelections();
                    const afterClearCount = selectedIngredients.size;
                    btnResume.click();
                    const afterResumeCount = selectedIngredients.size;
                    return {
                        initialDisplay,
                        afterClearCount,
                        afterResumeCount,
                        resumedItems: Array.from(selectedIngredients)
                    };
                })()""",
                'returnByValue': True
            })
            rc = resume_check.get('result', {}).get('value', {})
            print("   Resume Last Check:", rc)
            assert rc.get('initialDisplay') != 'none', "Resume button should be visible!"
            assert rc.get('afterClearCount') == 0, "Selected count after clear should be 0!"
            assert rc.get('afterResumeCount') > 0, "Selected count after resume should be > 0!"

            # Test Repeat Visit Greeting on Page Reload
            print("   Testing Repeat Visit Greeting on Page Reload...")
            await send('Page.reload')
            for _ in range(25):
                await asyncio.sleep(0.3)
                ready = await send('Runtime.evaluate', {'expression': 'document.readyState === "complete" && typeof getState === "function"', 'returnByValue': True})
                if ready.get('result', {}).get('value') is True:
                    break

            await asyncio.sleep(0.5)
            repeat_visit_check = await send('Runtime.evaluate', {
                'expression': """(() => {
                    const speechEl = document.getElementById('misae-speech');
                    const speech = speechEl ? speechEl.textContent.trim() : '';
                    const state = typeof getState === 'function' ? getState() : {};
                    return {
                        visits: state.visits,
                        speech
                    };
                })()""",
                'returnByValue': True
            })
            rvc = repeat_visit_check.get('result', {}).get('value') or {}
            print("   Repeat Visit Greeting Check:", rvc)
            assert rvc.get('visits') is not None and rvc.get('visits') >= 2, f"Visit counter did not increment on reload! Got: {rvc}"
            assert "Welcome back!" in rvc.get('speech', ''), f"Repeat visit greeting missing in speech bubble! Got: {rvc.get('speech')}"

            # Test Settings App: Clear Saved Data
            await send('Runtime.evaluate', {'expression': 'showPhoneScreen("settings")'})
            await asyncio.sleep(0.2)

            clear_check = await send('Runtime.evaluate', {
                'expression': """(() => {
                    resetState();
                    applyStateToUI();
                    const state = JSON.parse(localStorage.getItem('recipeRoulette.v1') || '{}');
                    return {
                        historyLen: (state.history || []).length,
                        favLen: (state.favorites || []).length,
                        resumeBtnDisplay: window.getComputedStyle(document.getElementById('btn-resume-ingredients')).display
                    };
                })()""",
                'returnByValue': True
            })
            cc = clear_check.get('result', {}).get('value', {})
            print("   Clear Saved Data Check:", cc)
            assert cc.get('historyLen') == 0, "History should be empty after reset!"
            assert cc.get('favLen') == 0, "Favorites should be empty after reset!"
            assert cc.get('resumeBtnDisplay') == 'none', "Resume button should be hidden after reset!"

            # Test Storage Disabled Simulation (Fallback to in-memory state without crashing)
            storage_disable_check = await send('Runtime.evaluate', {
                'expression': """(() => {
                    // Simulate blocked storage
                    const originalSet = Storage.prototype.setItem;
                    Storage.prototype.setItem = () => { throw new DOMException("QuotaExceededError or SecurityError", "QuotaExceededError"); };
                    
                    let memoryCheckSuccess = false;
                    try {
                        recordCookedRecipe({ name: "Emergency Test Noodles", time: "3 min", difficulty: "Easy" });
                        const state = getState();
                        memoryCheckSuccess = state.history.some(h => h.name === "Emergency Test Noodles");
                    } catch (e) {
                        memoryCheckSuccess = false;
                    } finally {
                        Storage.prototype.setItem = originalSet;
                    }
                    return memoryCheckSuccess;
                })()""",
                'returnByValue': True
            })
            sdc = storage_disable_check.get('result', {}).get('value')
            print("   Storage Blocked Simulation (In-Memory Fallback):", sdc)
            assert sdc is True, "In-memory state fallback failed when storage was blocked!"

            # Check 7: Contrast Ratios on Every Screen
            print("\n6. Evaluating WCAG AA Contrast Ratios (Target >= 4.5:1 for normal text)...")
            contrast_queries = [
                {"screen": "fridge", "name": "Speech Bubble Text", "selector": "#misae-speech"},
                {"screen": "fridge", "name": "Pantry Staples Label", "selector": ".pantry-label"},
                {"screen": "fridge", "name": "Pantry Staples Pill", "selector": ".pantry-strip .pill"},
                {"screen": "fridge", "name": "Pantry Staples Note", "selector": ".pantry-note"},
                {"screen": "fridge", "name": "Recipe Title", "selector": "#card-recipe-title"},
                {"screen": "fridge", "name": "Recipe Steps", "selector": ".recipe-steps-list li"},
                {"screen": "fridge", "name": "Shinchan Card Quote", "selector": "#card-shinchan-quote"},
                {"screen": "fridge", "name": "Mummy Verdict Seal", "selector": "#card-mummy-verdict .verdict-sub"},
                {"screen": "cookbook", "name": "Cookbook Dish Title", "selector": ".cooked-dish-title"},
                {"screen": "cookbook", "name": "Cookbook Dish Meta", "selector": ".cooked-dish-meta span"},
                {"screen": "cookbook", "name": "Cookbook Verdict Teal", "selector": ".cooked-dish-meta span.verdict-teal"},
                {"screen": "action-kamen", "name": "Kamen Stats Channel", "selector": ".kamen-stats .kamen-stat-item"},
                {"screen": "shiro", "name": "Shiro Speech Bubble", "selector": ".shiro-speech-bubble"},
                {"screen": "shiro", "name": "Polaroid Caption", "selector": ".polaroid-caption"},
                {"screen": "notes", "name": "Notepad Default Rule", "selector": ".notepad-list li"},
                {"screen": "weather", "name": "Weather Condition", "selector": ".weather-condition"},
                {"screen": "weather", "name": "Weather Primary Forecast", "selector": ".weather-primary-forecast"},
                {"screen": "weather", "name": "Weather Stat Box Value", "selector": ".stat-value"},
                {"screen": "weather", "name": "Weather Advice", "selector": ".weather-advice-box"},
                {"screen": "contacts", "name": "Contact Name", "selector": ".contact-name"},
                {"screen": "contacts", "name": "Contact Subtitle", "selector": ".contact-sub"},
                {"screen": "settings", "name": "Setting Title", "selector": ".settings-title"},
                {"screen": "settings", "name": "Setting Strong Label", "selector": ".setting-info strong"},
                {"screen": "settings", "name": "Setting Sub Label", "selector": ".setting-info span"},
            ]

            failing_contrasts = []
            results_contrast = []

            for item in contrast_queries:
                await send('Runtime.evaluate', {'expression': f'showPhoneScreen("{item["screen"]}")'})
                await asyncio.sleep(0.1)

                eval_expr = f"""(() => {{
                    const el = document.querySelector('{item["selector"]}');
                    if (!el) return null;
                    const style = window.getComputedStyle(el);
                    let bg = style.backgroundColor;
                    let p = el.parentElement;
                    while (p && (bg === 'rgba(0, 0, 0, 0)' || bg === 'transparent')) {{
                        bg = window.getComputedStyle(p).backgroundColor;
                        p = p.parentElement;
                    }}
                    return {{
                        color: style.color,
                        bg: bg,
                        fontSize: style.fontSize,
                        fontWeight: style.fontWeight
                    }};
                }})()"""
                res = await send('Runtime.evaluate', {'expression': eval_expr, 'returnByValue': True})
                val = res.get('result', {}).get('value')
                if val:
                    fg_rgba = parse_rgba(val['color'])
                    bg_rgba = parse_rgba(val['bg'])
                    ratio = calc_contrast_ratio(fg_rgba, bg_rgba)
                    status = "PASS" if ratio >= 4.5 else "WARN"
                    results_contrast.append({
                        "name": item["name"],
                        "screen": item["screen"],
                        "ratio": round(ratio, 2),
                        "status": status,
                        "fg": val['color'],
                        "bg": val['bg']
                    })
                    print(f"   [{status}] {item['screen'].upper()} - {item['name']}: {round(ratio, 2)}:1 (fg: {val['color']} on bg: {val['bg']})")
                    if ratio < 4.5:
                        failing_contrasts.append(item['name'])

            assert len(failing_contrasts) == 0, f"Contrast below 4.5:1 on: {failing_contrasts}"

            # Check 8: Capture Screenshots of every screen at 375px and 1366px
            print("\n7. Capturing screenshots of each screen at 375px and 1366px into screenshots/...")
            all_screens = ['home', 'fridge', 'chat', 'action-kamen', 'shiro', 'notes', 'cookbook', 'weather', 'contacts', 'settings']
            viewports_to_capture = [
                {'width': 375, 'height': 812, 'mobile': True, 'suffix': '375px'},
                {'width': 1366, 'height': 768, 'mobile': False, 'suffix': '1366px'}
            ]

            for vp in viewports_to_capture:
                await send('Emulation.setDeviceMetricsOverride', {
                    'width': vp['width'],
                    'height': vp['height'],
                    'deviceScaleFactor': 1,
                    'mobile': vp['mobile']
                })
                await asyncio.sleep(0.2)
                for sc in all_screens:
                    await send('Runtime.evaluate', {'expression': f'showPhoneScreen("{sc}")'})
                    await asyncio.sleep(0.15)
                    shot = await send('Page.captureScreenshot', {'format': 'png'})
                    if shot.get('data'):
                        filename = f"screenshots/{sc}_{vp['suffix']}.png"
                        with open(filename, 'wb') as f:
                            f.write(base64.b64decode(shot['data']))
                        print(f"   Saved: {filename}")

            # Check 9: Final Console & Network Error Assertions
            print("\n8. Checking final Console and Network errors...")
            print("   Console errors:", console_errors)
            print("   Network errors:", network_errors)
            assert len(console_errors) == 0, f"Found console errors: {console_errors}"
            assert len(network_errors) == 0, f"Found network errors: {network_errors}"

            print("\n🎉 ALL TESTS AND CONTRAST RATIO VERIFICATIONS PASSED CLEANLY (0 ERRORS)!")
    finally:
        proc.terminate()

if __name__ == '__main__':
    asyncio.run(run_comprehensive_test())
