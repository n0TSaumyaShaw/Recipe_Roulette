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

            # Check 1: Go to Home
            print("1. Navigating from chat intro to home screen...")
            nav_eval = await send('Runtime.evaluate', {'expression': '(() => { try { showPhoneScreen("home"); return { ok: true, active: document.getElementById("screen-home").classList.contains("active") }; } catch (e) { return { error: e.message, stack: e.stack }; } })()', 'returnByValue': True})
            print("   nav_eval:", nav_eval)
            await asyncio.sleep(0.3)

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
                {"screen": "shiro", "name": "Shiro Hero Description", "selector": ".shiro-hero-desc"},
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
