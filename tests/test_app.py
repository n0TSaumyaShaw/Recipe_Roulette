import asyncio
import websockets
import json
import urllib.request
import subprocess
import time

CHROME_PATH = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
PORT = 9455

async def run_comprehensive_test():
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
            except Exception as e:
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
                    # Track any console errors
                    if resp.get('method') == 'Runtime.exceptionThrown':
                        console_errors.append(resp.get('params', {}).get('exceptionDetails', {}).get('text', 'Unknown JS Error'))
                    elif resp.get('method') == 'Network.responseReceived':
                        res = resp.get('params', {}).get('response', {})
                        if res.get('status') >= 400:
                            network_errors.append(f"{res.get('status')} {res.get('url')}")
                    if resp.get('id') == msg_id:
                        return resp.get('result', {})

            await send('Page.enable')
            await send('Runtime.enable')
            await send('Network.enable')
            await send('Emulation.setDeviceMetricsOverride', {'width': 1280, 'height': 950, 'deviceScaleFactor': 1, 'mobile': False})

            # Check 1: Chat Intro & Avatar Path
            print("1. Checking Chat Intro & Avatar Image Paths...")
            pfp_check = await send('Runtime.evaluate', {
                'expression': """(() => {
                    const img = document.querySelector('.chat-header-pfp');
                    return {
                        src: img ? img.getAttribute('src') : null,
                        complete: img ? img.complete : false,
                        naturalWidth: img ? img.naturalWidth : 0
                    };
                })()""",
                'returnByValue': True
            })
            pfp_val = pfp_check.get('result', {}).get('value', {})
            print("   Chat Header Avatar:", pfp_val)
            assert "assets/images/avatars/misae-pfp.webp" in pfp_val.get('src', ''), "Avatar path incorrect!"

            # Check 2: Transition to Home Screen
            print("2. Transitioning to Home Screen...")
            await send('Runtime.evaluate', {'expression': 'transitionToApp()'})
            await asyncio.sleep(0.5)

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
            assert val_home.get('notchPresent') is False, "Notch should be completely removed!"

            # Check 3: Test Every Single App (All 10)
            apps = ['fridge', 'chat', 'action-kamen', 'chocobi', 'shiro', 'notes', 'cookbook', 'weather', 'contacts', 'settings']
            print(f"3. Testing all {len(apps)} Phone Apps...")
            for app in apps:
                await send('Runtime.evaluate', {'expression': f'showPhoneScreen("{app}")'})
                await asyncio.sleep(0.2)
                cur = await send('Runtime.evaluate', {'expression': 'currentPhoneScreen', 'returnByValue': True})
                assert cur.get('result', {}).get('value') == app, f"Failed navigating to app: {app}"
                print(f"   ✓ App [{app}] opened successfully")
            
            # Back to home
            await send('Runtime.evaluate', {'expression': 'showPhoneScreen("home")'})
            await asyncio.sleep(0.3)
            import base64
            ss_home = await send('Page.captureScreenshot', {'format': 'png'})
            if ss_home.get('data'):
                with open('tests/preview_home_grid.png', 'wb') as f:
                    f.write(base64.b64decode(ss_home['data']))
                print("   Saved screenshot: tests/preview_home_grid.png")

            # Check 4: Test Mute Button Synchronization (Header & Fridge)
            print("4. Testing Sound Mute Synchronization across Header and Fridge...")
            # Click Header sound toggle
            await send('Runtime.evaluate', {'expression': 'document.getElementById("btn-sound-toggle").click()'})
            sync1 = await send('Runtime.evaluate', {
                'expression': """(() => ({
                    soundEnabled,
                    mainIcon: document.getElementById('sound-icon').textContent,
                    fridgeIcon: document.getElementById('sound-icon-fridge').textContent
                }))()""",
                'returnByValue': True
            })
            print("   After header toggle (mute):", sync1.get('result', {}).get('value'))
            s1 = sync1.get('result', {}).get('value', {})
            assert s1.get('soundEnabled') is False and s1.get('mainIcon') == '🔇' and s1.get('fridgeIcon') == '🔇', "Sound mute out of sync!"

            # Click Fridge sound toggle (unmute)
            await send('Runtime.evaluate', {'expression': 'document.getElementById("btn-sound-toggle-fridge").click()'})
            sync2 = await send('Runtime.evaluate', {
                'expression': """(() => ({
                    soundEnabled,
                    mainIcon: document.getElementById('sound-icon').textContent,
                    fridgeIcon: document.getElementById('sound-icon-fridge').textContent
                }))()""",
                'returnByValue': True
            })
            print("   After fridge toggle (unmute):", sync2.get('result', {}).get('value'))
            s2 = sync2.get('result', {}).get('value', {})
            assert s2.get('soundEnabled') is True and s2.get('mainIcon') == '🔊' and s2.get('fridgeIcon') == '🔊', "Sound unmute out of sync!"

            # Check 5: Test Recipe Roulette & data/recipes.json load
            print("5. Testing Recipe Roulette in Fridge Screen...")
            await send('Runtime.evaluate', {'expression': 'showPhoneScreen("fridge")'})
            await asyncio.sleep(0.3)

            # Check recipes loaded from data/recipes.json
            recipe_count = await send('Runtime.evaluate', {'expression': 'allRecipes.length', 'returnByValue': True})
            cnt = recipe_count.get('result', {}).get('value', 0)
            print(f"   Loaded recipes count from data/recipes.json: {cnt}")
            assert cnt >= 50, f"Expected 50 recipes, got {cnt}!"

            # Test Cook: select eggs, onion, bread
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

            ss_fridge = await send('Page.captureScreenshot', {'format': 'png'})
            if ss_fridge.get('data'):
                with open('tests/preview_fridge_recipe.png', 'wb') as f:
                    f.write(base64.b64decode(ss_fridge['data']))
                print("   Saved screenshot: tests/preview_fridge_recipe.png")

            # Check 6: Verify Cookbook logged the cooked recipe
            await send('Runtime.evaluate', {'expression': 'showPhoneScreen("cookbook")'})
            await asyncio.sleep(0.3)
            logged = await send('Runtime.evaluate', {'expression': 'sessionCookbook.map(r => r.name)', 'returnByValue': True})
            print("   Cookbook logged dishes:", logged.get('result', {}).get('value'))
            assert len(logged.get('result', {}).get('value', [])) > 0, "No dishes recorded in session cookbook!"

            # Check 7: Test World Kitchen Toggle
            print("7. Testing World Kitchen Toggle...")
            await send('Runtime.evaluate', {'expression': 'document.getElementById("btn-mode-world").click()'})
            km = await send('Runtime.evaluate', {'expression': 'kitchenMode', 'returnByValue': True})
            assert km.get('result', {}).get('value') == 'world', "Kitchen mode did not switch to world!"
            print("   World Kitchen Mode toggled successfully")

            # Check 8: Test Anger Meter 100% Rage
            print("8. Testing Mom's 100% Anger Rage Modal...")
            await send('Runtime.evaluate', {'expression': 'increaseMomAnger(100)'})
            await asyncio.sleep(0.5)
            rage_state = await send('Runtime.evaluate', {
                'expression': """(() => ({
                    modalVisible: !document.getElementById('mom-rage-modal').classList.contains('hidden'),
                    phoneShaking: document.getElementById('comic-phone').classList.contains('shake-intense')
                }))()""",
                'returnByValue': True
            })
            print("   Rage State:", rage_state.get('result', {}).get('value'))
            assert rage_state.get('result', {}).get('value', {}).get('modalVisible') is True, "Rage modal did not appear!"

            # Calm Mom down
            await send('Runtime.evaluate', {'expression': 'document.getElementById("btn-rage-calm").click()'})
            await asyncio.sleep(0.3)

            # Check 9: Notification Banner
            print("9. Testing Notification Banner...")
            await send('Runtime.evaluate', {'expression': 'triggerRandomNotification()'})
            notif_shown = await send('Runtime.evaluate', {
                'expression': 'document.getElementById("phone-notif").classList.contains("show")',
                'returnByValue': True
            })
            print(f"   Notification banner active: {notif_shown.get('result', {}).get('value')}")

            # Check 10: Multi-viewport Verification (1920x1080, 1366x768, 375x812)
            print("10. Testing Viewports: 1920x1080, 1366x768, 375x812...")
            viewports = [
                {'name': 'desktop_1920x1080', 'width': 1920, 'height': 1080, 'mobile': False},
                {'name': 'laptop_1366x768', 'width': 1366, 'height': 768, 'mobile': False},
                {'name': 'mobile_375x812', 'width': 375, 'height': 812, 'mobile': True}
            ]

            import base64
            for vp in viewports:
                await send('Emulation.setDeviceMetricsOverride', {
                    'width': vp['width'],
                    'height': vp['height'],
                    'deviceScaleFactor': 1,
                    'mobile': vp['mobile']
                })
                await asyncio.sleep(0.3)
                
                # Check for horizontal overflow on key phone elements & side panel visibility
                panel_check = await send('Runtime.evaluate', {
                    'expression': """(() => {
                        const phone = document.getElementById('comic-phone');
                        const viewport = document.getElementById('phone-screens-viewport');
                        const cardActions = document.querySelector('.card-actions');
                        const leftPanel = document.querySelector('.side-panel-left');
                        const rightPanel = document.querySelector('.side-panel-right');
                        const leftDisplay = leftPanel ? window.getComputedStyle(leftPanel).display : 'none';
                        const rightDisplay = rightPanel ? window.getComputedStyle(rightPanel).display : 'none';
                        return {
                            phoneOverflow: phone ? phone.scrollWidth > phone.clientWidth : false,
                            cardActionsOverflow: cardActions ? cardActions.scrollWidth > cardActions.clientWidth : false,
                            sidePanelsVisible: leftDisplay !== 'none' && rightDisplay !== 'none'
                        };
                    })()""",
                    'returnByValue': True
                })
                of_res = panel_check.get('result', {}).get('value', {})
                print(f"    Viewport [{vp['name']}]: Check:", of_res)
                assert of_res.get('phoneOverflow') is False, f"Phone overflowed horizontally at {vp['name']}!"
                if vp['width'] >= 1024:
                    assert of_res.get('sidePanelsVisible') is True, f"Side panels should be visible at {vp['name']}!"
                else:
                    assert of_res.get('sidePanelsVisible') is False, f"Side panels should be hidden at {vp['name']}!"

                # Take screenshot
                ss = await send('Page.captureScreenshot', {'format': 'png'})
                if ss.get('data'):
                    with open(f"tests/preview_{vp['name']}.png", 'wb') as f:
                        f.write(base64.b64decode(ss['data']))
                    print(f"    Saved screenshot: tests/preview_{vp['name']}.png")

            # Check 11: Test Side Panel "TRY IT" Button (Curd Rice Tadka)
            print("11. Testing Side Panel 'TRY IT' Button...")
            await send('Emulation.setDeviceMetricsOverride', {'width': 1920, 'height': 1080, 'deviceScaleFactor': 1, 'mobile': False})
            await asyncio.sleep(0.3)
            await send('Runtime.evaluate', {'expression': 'document.getElementById("btn-side-try").click()'})
            await asyncio.sleep(2.5)
            side_try_result = await send('Runtime.evaluate', {
                'expression': """(() => ({
                    screen: currentPhoneScreen,
                    title: document.getElementById('card-recipe-title').textContent.trim(),
                    displayActive: document.getElementById('recipe-display').classList.contains('active')
                }))()""",
                'returnByValue': True
            })
            val_side_try = side_try_result.get('result', {}).get('value', {})
            print("    Side 'TRY IT' Result:", val_side_try)
            assert val_side_try.get('screen') == 'fridge', "Screen did not switch to fridge!"
            assert val_side_try.get('displayActive') is True, "Recipe display not active after TRY IT!"

            # Check 12: Final Console & Network Error Assertions
            print("12. Checking Console and Network Errors...")
            print("    Console errors detected:", console_errors)
            print("    Network errors (4xx/5xx) detected:", network_errors)
            assert len(console_errors) == 0, f"Found console errors: {console_errors}"
            assert len(network_errors) == 0, f"Found network 404/500 errors: {network_errors}"

            print("\n🎉 ALL TESTS PASSED WITH 0 CONSOLE ERRORS AND 0 NETWORK ERRORS!")
    finally:
        proc.terminate()

if __name__ == '__main__':
    asyncio.run(run_comprehensive_test())
