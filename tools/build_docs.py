"""Build the documentation website and its printable engineering guide."""
from pathlib import Path
from html import escape
import json, shutil

ROOT=Path(__file__).resolve().parents[1]; DOCS=ROOT/'docs'; DOCS.mkdir(exist_ok=True)
# Shared editorial content keeps the website and PDF consistent.
CHAPTERS=[
('overview','Project overview',[
('Purpose and release boundary',[
'GPIO Viewer for Mzansi Connect is an additional, read-only interface for the Zepkvor ZEK-03 ESP32-C3 development board with an integrated 0.42-inch OLED. It was requested as a comparison option before deciding whether to remove the existing GPIO Viewer. This release deliberately retains the original viewer, its server and sampling service. The new visual layout is based on the supplied product photograph rather than a generic ESP32-C3 SuperMini or DevKitM-1.',
'The integration is Mzansi firmware 2.2.6-c3-zek03-viewer, Android app 1.3.0 (versionCode 4), and custom viewer 1.0.0. The standalone repository contains the reusable viewer, generated board profile, integration instructions, tests and documentation. Device-specific Wi-Fi secrets and signing keys are excluded. The existing complete Mzansi project remains the place to build the configured device firmware and Android app.']),
('What this release provides',[
'The new page has a photographed-layout purple-board SVG, selectable header pins, state highlighting, GPIO numbers, digital HIGH/LOW values, raw PWM/ADC values, declared-mode information, application assignments and capability notes. Power rails are displayed with separate styling and never presented as programmable GPIO or measured voltage channels. A generic pin list provides an alternative view.',
'Connection status, stale-data handling, automatic reconnect, manual reconnect, pause/resume and a rolling chart make the viewer useful during diagnosis. All device-page CSS, JavaScript, SVG and board metadata are embedded in one gzip-compressed asset. The new page therefore works without downloading GitHub Pages assets. The original upstream viewer still has its own remote-asset requirements.']),
('What is not being claimed',[
'A sampled pin value is not an oscilloscope measurement. It cannot decode fast UART or SPI traffic at a 250 ms interval, establish GPS location validity, demonstrate radio ACKs, or prove RF range. A diagram matching the visible product layout is not a dimensioned manufacturing drawing. The OLED is represented visually but is not initialized by the viewer.',
'A professional result separates implementation evidence from physical verification. Browser fixtures prove UI behavior under controlled data; compilation proves the build fits and links; a real device check proves only the operations actually observed. The verification page records those categories separately rather than describing every feature as hardware-verified.'])]),
('setup','Installation and daily operation',[
('Start from a recoverable device',[
'Keep USB recovery available before any firmware update. Compile for the correct ESP32-C3 target, flash size, USB CDC setting and partition layout. The matching application .bin is the image for the dashboard OTA route; an Android APK, source .ino or merged flash image is not interchangeable with it. The existing NVS settings and version-history mechanism are retained.',
'After flashing or restarting, leave the device powered for two minutes. USB reappearance is not the same as completed startup. First check the main dashboard, the firmware version and saved settings; then check GPIO telemetry. If Wi-Fi is unavailable, use the recovery hotspot in normal mode. Do not repeatedly reboot during the startup window.']),
('Enable the shared telemetry service',[
'Open Mzansi Dashboard, select GPIO Live, enable GPIO Viewer and save the settings. This existing feature switches the board to station-only diagnostic mode on restart. The recovery hotspot is temporarily disabled in that mode. Both viewer interfaces depend on this same service; selecting the new menu option does not silently enable it.',
'Wait another two minutes, then use the LAN IP on port 80 for Mzansi and port 8080 for the original GPIO Viewer. The existing 45-second disconnected-Wi-Fi failsafe disables diagnostic mode and restarts into recovery mode. It tests association state, not every possible failure of browser access, router routing or multicast discovery.']),
('Android flow and direct browser access',[
'The required order remains IP address, dashboard mode, API key, then open. The mode menu contains Mzansi Dashboard, GPIO Viewer for Mzansi Connect, and the original GPIO Viewer. The new option opens http://DEVICE_IP/gpio-mzansi. The original remains http://DEVICE_IP:8080/. Enter the key configured for the device; this public guide does not distribute a household device key.',
'The Android app validates the key against /api/status before opening the chosen page. The new page uses the existing same-origin sessionStorage workflow; returning to the app menu clears stored browser data. Direct-browser users enter the IP and key in the viewer page. The password field is cleared after a successful connection. The session can be explicitly cleared with Disconnect.']),
('Using the controls',[
'Click a pin hole or its table row, or use keyboard focus and Enter/Space. The inspector shows its physical side and position, GPIO alias where applicable, received value, declared mode, capability hints and current Mzansi assignment. The chart stores the last 60 display observations for the selected GPIO. With 500 ms chart collection this is about 30 seconds once filled; it is not the separate GPS history buffer.',
'Pause display freezes displayed GPIO values while the stream continues to send connection heartbeats. Resume opens a fresh stream so values changed during the pause are recovered through the upstream reset/snapshot behavior. Generic pin list hides the board drawing while preserving the table and inspector. Reconnect validates the device again; Disconnect closes the stream and removes the session key.'])]),
('hardware','Board identification and evidence',[
('Read the drawing in the correct orientation',[
'Look at the front, with the OLED facing you and USB-C downward. The purple rectangular PCB has eight through-hole header positions per side, RST at top-left and BOOT at top-right. The display occupies the upper-middle area; the USB-C shell projects below the PCB. The drawing includes the central top component, display flex area, small components, power indicator and IO8 user-LED markings visible in the photograph.',
'The supplied photograph is the authority for physical label order. From top to bottom, the left side is 3, 4, 5, 6, 7, 8, 9, 10. The right side is 0, 1, 2, TX, RX, 3V3, GND, 5V. The view is not mirrored. Digital GPIO numbers and rail names are stored separately so the renderer cannot accidentally turn 3V3 or 5V into live GPIO channels.']),
('TX and RX evidence',[
'The current project receives readable GPS NMEA when GPS TXD is connected to the board RX-labelled header and the ESP32 UART listens on GPIO20 at 9600 baud. The project transmits on GPIO21 through the TX-labelled header. Espressif Arduino-ESP32 3.3.12 also defines the generic C3 TX/RX aliases as 21/20. Together these support the operational mapping used here.',
'A generic core alias alone does not prove a vendor header trace. No authoritative Zepkvor ZEK-03 schematic was found during this work. The board metadata explicitly describes TX=21 and RX=20 as project wiring/test evidence rather than manufacturer certification. If a different physical revision fails the same test, check its traces or obtain its exact schematic before changing the mapping.']),
('OLED internals: verified versus unknown',[
'The listing and supplied product description identify a 0.42-inch integrated OLED. The photograph establishes its placement, not its controller or pixel matrix. For this exact ZEK-03, controller model, resolution, I2C SDA, I2C SCL, I2C address and shared external-header wiring are all recorded as unknown (null) in board.json.',
'A separate maintainer project documents GPIO5/6 OLED I2C on a similar mini C3 OLED board and explicitly warns that SPI and OLED I2C can conflict. That is useful research evidence for a hypothesis, not proof that the ZEK-03 is electrically identical. The current Mzansi radio already uses GPIO5 as MISO and GPIO6 as MOSI. Do not run an I2C scan or initialize a guessed display configuration over those active radio pins.',
'To resolve the uncertainty, obtain a schematic explicitly naming ZEK-03 and its revision, inspect continuity on an unpowered board with attached modules disconnected, then test an isolated display sketch using the verified pins. An I2C acknowledgement can establish that something responds at an address; it does not by itself identify the controller or pixel resolution. Update the metadata only with the resulting evidence.']),
('Electrical and capability notes',[
'ESP32-C3 GPIO uses 3.3 V logic. The 5V header is a supply rail, not permission to drive a GPIO with 5 V. Power and ground entries in this viewer do not measure their voltage. Use an appropriate meter for supply checks. The nRF24 PA/LNA needs a stable regulated 3.3 V supply, shared ground and local decoupling; digital activity alone does not establish adequate power.',
'GPIO2, GPIO8 and GPIO9 are C3 strapping pins, sampled during reset. External loads must preserve valid boot levels. GPIO0-4 have ADC1 capability; GPIO5 is associated with ADC2 and C3-specific restrictions. Capability hints describe silicon facilities, not a guarantee that the current application has configured or can safely repurpose that function. The viewer does not offer output toggles.'])]),
('architecture','Architecture and live protocol',[
('Why there are two interfaces',[
'The workspace is an Arduino-ESP32 firmware project with an embedded synchronous WebServer dashboard and an Android Java WebView app. It did not contain the complete upstream Vue development repository. The installed GPIOViewer 1.7.1 library serves port 8080 and normally loads its web application and board assets from the upstream GitHub Pages site. The upstream registry is boards.json with image and indicator-file paths; indicator files position GPIO IDs over a board image.',
'The new implementation keeps that service intact. Mzansi serves /gpio-mzansi on port 80 as a compressed PROGMEM byte array. The browser reads existing endpoints on the same host at port 8080. The repository also provides boards.json and zek-03-indicators.json in the upstream registration schema, but it does not claim to have changed the upstream public board menu. A separate upstream contribution would require its maintainers to accept those assets.']),
('The wire contract',[
'The browser opens EventSource at http://HOST:8080/events. A gpio-state event contains a JSON object keyed by GPIO number. Each value has s, v and t. For example, {"3":{"s":256,"v":1,"t":0}} means GPIO3 was sampled digital HIGH. Type t=0 is digital, t=1 is PWM, t=2 is ADC. The original raw value v is displayed; s is the library visualization value and is not a voltage.',
'Frames are deltas: only changed pins may be present. applyFrame validates numeric fields, ignores malformed entries and merges into the existing cache. Replacing the entire cache with each frame would incorrectly erase unchanged GPIO values. The upstream library resets its state cache when a stream client connects, causing the next sample to repopulate values. The new viewer clears its display cache on opening a fresh stream so old values are not presented as new observations.',
'The free_heap event carries formatted heap text and also provides an idle heartbeat. /pinmodes returns declared pin/mode entries; modes are shown when available, otherwise Not declared. These declarations are bookkeeping, not a full hardware peripheral-mux decoder. In the current firmware, the bridge declares active UART/SPI/buzzer/LED pins without reapplying pinMode to already running peripherals.']),
('Staleness, reconnection and chart semantics',[
'On an EventSource error, the connection is closed, current GPIO display becomes stale, and an automatic reconnect is scheduled after 2.5 seconds. A six-second heartbeat gap also marks values stale. A reconnect generation number prevents obsolete asynchronous requests from updating a newer connection. The page closes its source and timers when leaving or disconnecting.',
'The chart samples the latest received cache every 500 ms while not paused. Values can repeat because the GPIO has not changed. A digital trace is normalized to LOW/HIGH; ADC and PWM traces are scaled to the selected recent maximum. This is a display of sampled observations, not a uniformly timed electrical acquisition. Browser delays, Wi-Fi congestion and the firmware sampler all affect it.']),
('Backend limitations inherited from upstream',[
'GPIOViewer 1.7.1 polls GPIOs and may infer analog/PWM type. Its core-3 ADC path can classify a zero ADC reading as digital LOW because it only chooses analog when the reading is nonzero. This UI displays the reported type honestly and cannot recover an unreported analog zero classification. Declared output/input modes are not the same as actual peripheral function or packet content.',
'Both interfaces share the existing sampling workload. The new UI does not add another GPIO task or change the sampling interval. Multiple simultaneous EventSource clients still add sockets and delivery overhead; use one viewer at a time on a constrained board when comparing. An upstream client connection can reset the shared library state cache and cause a refresh in other clients.'])]),
('led','Onboard network status LED',[
('Pattern meanings',[
'Home Wi-Fi connected: two short pulses, 160 ms on, 180 ms off, 160 ms on, then off for the remainder of an eight-second cycle. The double pattern starts immediately after a state transition is processed. Repeating it makes the current network state visible without requiring someone to watch the exact moment of connection.',
'Home Wi-Fi unavailable with the recovery hotspot active: a long 1,800 ms pulse followed by 1,200 ms off, repeating. During the initial connection window the LED remains off; the fallback pattern is used when the startup connection window has elapsed or no home password is configured and an AP is actually running. In station-only diagnostic mode, the long hotspot pattern cannot appear until the existing recovery restart restores the AP.']),
('Implementation and electrical assumptions',[
'The photo shows an IO8 marking beside a user indicator. This supports selecting physical GPIO8; the firmware does not use LED_BUILTIN because the generic C3 variant defines a synthetic addressable-RGB alias. The LED is initialized after boot and its state is updated from a pure timing function in network_led.h. GPIO8 is also registered as OUTPUT in the viewer bridge so it is not treated as an unassigned analog input.',
'Active-low behavior is an explicit assumption for this board revision pending a visual hardware check. NETWORK_LED_ACTIVE_LOW controls it in one place. If the flashes are inverted or the indicator is almost continuously lit, verify polarity on the actual board and change that constant. Neither the product photo nor software readback can prove LED polarity or physical illumination. The always-powered PWR indicator cannot generally be blinked by firmware.']),
('Non-blocking operation and what connection means',[
'No delay calls are used for the pattern. Unsigned elapsed time and modulo arithmetic determine the phase, and GPIO8 is updated during the normal loop. The header includes compile-time assertions at timing boundaries. GPS parsing, radio work and dashboard servicing continue while a pattern is in progress, although an already-blocking operation elsewhere in the application can still delay loop updates.',
'The double flash indicates the ESP32 is associated with home Wi-Fi. It does not prove Internet connectivity, a phone is connected to the same network, or the Android app is open. The long flash indicates a recovery AP is configured and running, not that a phone has joined it. The existing same-Wi-Fi IP notification service remains separate and continues to use discovery and boot identifiers.'])]),
('security','Network and security model',[
('Where the key helps',[
'The new page checks the supplied device API key using /api/status on the main server before opening live monitoring. The key is sent in the existing X-Device-Key header, never in a URL. The Android integration validates the same key before loading the page. The reusable repository and hosted demo contain no configured household device key.',
'This check is not end-to-end telemetry authentication. GPIOViewer 1.7.1 independently serves /events and metadata on port 8080 with permissive CORS and no API-key check. Anyone who can reach that service can access it directly. The main HTTP connection also lacks TLS, so the application key does not provide confidentiality against an observer on the network.']),
('Session and publishing boundaries',[
'The browser retains the key in sessionStorage for the current device origin. Disconnect deletes it. The Android menu return clears WebStorage and uses no native JavaScript bridge. These are useful session hygiene measures, not substitutes for a stronger transport/authentication design. Device-origin scripts can access sessionStorage, so it must remain free of injected or untrusted content.',
'The public GitHub Pages site is documentation plus an explicitly labelled simulated demo. It does not run a device proxy, collect credentials or contact an ESP32. Use the page served over local HTTP by the board for live monitoring. Loading a public HTTPS page and trying to contact private HTTP hardware encounters browser mixed-content, private-network and CORS boundaries; the demo is not advertised as bypassing them.']),
('Operational precautions',[
'Use diagnostic mode on a trusted local network, then disable it when finished. Do not forward port 8080 from the router to the Internet. Keep the original viewer available for comparison and USB available for recovery. If stronger security is later required, authenticate the telemetry backend itself and design transport/session handling together; placing a password form in front of an open stream cannot accomplish that.'])]),
('development','Source map, builds and extending support',[
('Source responsibilities',[
'web/template.html contains the handwritten UI and connection lifecycle. web/telemetry.js implements the small pure delta parser and value formatter. tools/build_assets.py is the single source of physical pin positions, board metadata and SVG construction; it embeds the page and emits deterministic gzip bytes. web/index.html, web/board.json and web/zek-03.svg are generated outputs, not independent sources to edit.',
'boards.json and zek-03-indicators.json mirror the upstream registry/overlay format for reuse. integration.md explains the Mzansi WebServer route and Android mode changes. integration/network_led.h contains the timing function. tests/telemetry.test.js tests malformed inputs and delta semantics. tests/browser.test.cjs drives a real browser against controlled device fixtures and captures desktop/mobile screenshots.']),
('Repeatable build sequence',[
'Run python tools/build_assets.py from the standalone repository or its parent workspace. It creates integration/mzansi_gpio_html.h; when the neighboring main Mzansi sketch exists, it also updates that sketch header. Run node tests/telemetry.test.js for protocol checks. Install the pinned npm development dependency and run npm run test:browser for the browser fixture suite. A Windows Edge installation is used by the current test runner; the documented BROWSER_PATH override supports another installed Chromium executable.',
'For the full Mzansi workspace, compile the main sketch with ESP32 core 3.3.12 and the esp32:esp32:esp32c3:CDCOnBoot=cdc target. Keep GPIOViewer 1.7.1 pinned, along with the installed AsyncTCP and ESPAsyncWebServer versions. The bridge deliberately isolates their async headers from the synchronous WebServer. The generated asset is compressed to conserve the already limited application partition headroom.',
'Android is built from Android/MzansiConnect using its Gradle wrapper. App 1.3.0 retains SDK 34 targeting, minimum SDK 26 and the existing discovery service. Run assembleDebug and lintDebug; a debug-signed APK is for direct installation, not a Play Store production release. Preserve signing continuity when updating an installed app.']),
('Adding evidence or another board',[
'Change physical pin order only in the builder after checking the correct orientation against board-specific evidence. Keep stable physical IDs (side and position), displayed labels and numeric GPIO IDs distinct. Set GPIO to null for supply rails. If a TX/RX alias is unknown, preserve the printed alias and omit a numeric assignment until verified rather than showing a convincing but unsupported value.',
'When OLED wiring is established for an exact revision, record controller, resolution, SDA, SCL, address, shared headers, source and verification method. Plan conflicts with the radio before adding display initialization. A board-specific configuration should be data driven and should never silently borrow defaults from a visually similar board. Rebuild assets, run the protocol and browser checks, then verify the affected path on hardware.'])]),
('troubleshooting','Troubleshooting and acceptance',[
('Find the failing layer',[
'No new menu option: verify Android app 1.3.0 and firmware 2.2.6 are actually installed; a successful local build does not update a device by itself. A 404 at /gpio-mzansi usually means older firmware or the wrong host/port. The new page is on port 80; the original is on 8080. Check version history and wait the full startup window after installing.',
'The new page opens but says the service is off: enable GPIO Live in Mzansi Dashboard and allow the required restart. If diagnostic mode immediately disappears, inspect home Wi-Fi association and the 45-second recovery fallback. If the original viewer works but the new one fails, inspect /api/status authorization, browser console and the local route; if both streams fail, start with the shared port 8080 service and network reachability.',
'Values are stale or reconnecting: inspect Wi-Fi strength, router client isolation and the exact IP. Stale display is preferable to showing an old value as current. Heap text but few GPIO updates can simply mean the pins are unchanged because frames carry deltas. Not declared means mode metadata was unavailable; it does not mean the pin cannot function.']),
('Interpret signals correctly',[
'A UART RX pin may look HIGH most of the time because UART idles HIGH and 250 ms sampling misses short bit periods. Fast SPI also cannot be decoded from this display. If GPS has zero bytes, check GPS TXD to the RX-labelled header/GPIO20, common ground, power and baud. If NMEA arrives but there is no fix, inspect sky view and navigation validity rather than changing a proven UART mapping.',
'If the nRF24 is not detected, investigate its regulated supply, connector orientation, CSN/CE mapping and SPI wiring. A toggling SCK is not proof the radio answered. Do not initialize guessed OLED I2C pins on top of the active SPI bus. If a power rail is selected, the inspector correctly says it is not measured; use a meter.',
'If the network LED does not look as described, distinguish the power LED from the IO8 user LED. Verify the board revision and active level. A software HIGH or LOW observed on GPIO8 can confirm the requested output waveform but cannot verify that an actual LED lights. A long pulse should appear only in recovery-AP state; station-only mode has no active AP until recovery is restored.']),
('Acceptance checklist before removing the original',[
'Confirm the physical pin drawing against the supplied photo and check all 16 external labels. Open each of the three Android modes. Check API-key rejection, enabled/disabled service messaging, and direct browser sign-in. Compare the new view with the original on the same device without assuming exact frame timing across two concurrent clients.',
'Select a real configured output such as the onboard status LED and verify the reported mode/value. Test a known LOW and HIGH condition without shorting outputs or touching active SPI/UART pins. Disconnect and restore Wi-Fi to confirm stale state and reconnect. Pause and resume after a value changes, and confirm the refreshed value. Check phone portrait layout, keyboard selection and power-rail treatment.',
'After flashing, verify the reported firmware version, one new version-history entry, retained settings and ongoing GPS parsing. Confirm the IP notification watcher still reports a new boot. Observe the LED physically for connected and fallback patterns. Only then decide whether the new viewer satisfies daily use; keeping the original for comparison is part of this release, not an unfinished removal.'])]),
]

REFERENCES=[
('GPIOViewer 1.7.1 source','https://github.com/thelastoutpostworkshop/gpio_viewer/tree/v1.7.1','Primary source for EventSource /events, gpio-state delta format, pinmodes, CORS, sampling and STA-only service behavior.'),
('Upstream board registry','https://github.com/thelastoutpostworkshop/microcontroller_devkit/blob/main/gpio_viewer_1_5/boards.json','Existing board names, images and indicator-file registration format. This project does not claim an accepted upstream addition.'),
('Espressif Arduino C3 aliases, core 3.3.12','https://github.com/espressif/arduino-esp32/blob/3.3.12/variants/esp32c3/pins_arduino.h','TX=21/RX=20 core aliases; also demonstrates why the generic RGB LED alias is not assumed to identify the photographed LED circuitry.'),
('ESP32-C3 datasheet','https://www.espressif.com/sites/default/files/documentation/esp32-c3_datasheet_en.pdf','Silicon GPIO, ADC and strapping behavior. A chip datasheet is not a ZEK-03 PCB schematic.'),
('Arduino-ESP32 UART API','https://docs.espressif.com/projects/arduino-esp32/en/latest/api/serial.html','Explicit UART RX/TX routing and serial configuration.'),
('Similar mini C3 OLED board maintainer project','https://github.com/sigmdel/mini_esp32c3_oled_sketches','Primary observations for that maintainer\'s board, including 5/6 OLED I2C and potential SPI conflicts; not accepted as ZEK-03 manufacturer evidence.'),
('MDN EventSource','https://developer.mozilla.org/en-US/docs/Web/API/EventSource','Browser event-stream lifecycle and named events.'),
('Android WebView guide','https://developer.android.com/develop/ui/views/layout/webapps/webview','WebView application behavior and JavaScript integration considerations.'),
('Android network security configuration','https://developer.android.com/privacy-and-security/security-config','Cleartext policy and network trust configuration.'),
('GitHub Pages publishing sources','https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site','Publishing the /docs site from the main branch.'),
]

CSS='''*{box-sizing:border-box}body{margin:0;background:#0b1220;color:#e9f1f9;font-family:system-ui,-apple-system,sans-serif;line-height:1.65}a{color:#65e1d0;text-decoration:none}a:hover{text-decoration:underline}header,main,footer{max-width:1150px;margin:auto;padding:25px}header{display:flex;justify-content:space-between;gap:20px;border-bottom:1px solid #29394d}nav{display:flex;flex-wrap:wrap;gap:18px}.eyebrow{font-size:12px;letter-spacing:2px;color:#62dfcd;font-weight:750}h1{font-size:clamp(32px,6vw,64px);line-height:1.12;letter-spacing:-1.8px}h2{font-size:25px;margin-top:35px}p{color:#acbdcf}article{max-width:850px}article h1{font-size:42px}.hero{display:grid;grid-template-columns:1.25fr 1fr;align-items:center;gap:30px;padding:45px 0}.hero img{width:100%}.buttons{display:flex;flex-wrap:wrap;gap:12px;margin:24px 0}.button{border:1px solid #416175;background:#162c3d;border-radius:8px;padding:12px 18px;display:inline-block}.primary{background:#64dfce;color:#0a2b30;font-weight:750}.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}.card{background:#121f31;border:1px solid #2c3d52;padding:22px;border-radius:13px}.card h2{margin-top:0;font-size:20px}.callout{border-left:3px solid #dcaa6b;padding:12px 20px;background:#162232;margin:25px 0}table{width:100%;border-collapse:collapse;font-size:14px}th,td{text-align:left;padding:10px;border-bottom:1px solid #304258}th{color:#65dfce}footer{font-size:12px;color:#91a8bf;border-top:1px solid #29394d;margin-top:50px}code{color:#e2d5ff}img{max-width:100%}.sectionnav{display:flex;gap:12px;flex-wrap:wrap;margin-top:35px}.sectionnav a{border:1px solid #304258;padding:8px 12px;border-radius:8px}@media(max-width:750px){header{display:block}nav{margin-top:15px}.hero{display:block;padding:20px 0}.hero img{max-height:400px}.cards{grid-template-columns:1fr}header,main,footer{padding:20px}article h1{font-size:33px}}'''

def shell(title,body):
 return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="ZEK-03 board support, local GPIO monitoring and Mzansi Connect engineering documentation"><title>{escape(title)} | Mzansi Connect</title><link rel="stylesheet" href="site.css"></head><body><header><a href="index.html" class="eyebrow">MZANSI CONNECT / GPIO VIEWER</a><nav><a href="setup.html">Setup</a><a href="hardware.html">Hardware</a><a href="architecture.html">Architecture</a><a href="demo.html?demo=1">Demo</a><a href="https://github.com/SkylineITCloud/gpio-viewer-mzansi-connect">Source</a></nav></header><main>{body}</main><footer>Viewer 1.0.0 · Firmware integration 2.2.6 · Android 1.3.0 · 18 November 2026<br>Independent project. No manufacturer endorsement. Hosted demo values are simulated; use the device-served page for live data.</footer></body></html>'

def build_site():
 (DOCS/'site.css').write_text(CSS,encoding='utf-8');(DOCS/'.nojekyll').touch()
 shutil.copy2(ROOT/'web/zek-03.svg',DOCS/'zek-03.svg')
 demo=(ROOT/'web/index.html').read_text(encoding='utf-8')
 # The public page is demonstration-only regardless of its query string.
 demo=demo.replace("const preview=new URLSearchParams(location.search).get('demo')==='1';","const preview=true;")
 demo=demo.replace('<a class="button" id="dashboard" href="/">Dashboard</a>','<a class="button" id="dashboard" href="index.html">Documentation</a>')
 demo=demo.replace("function links(){ $('dashboard').href=base()+'/';$('original').href=base()+':8080/'; }","function links(){ $('dashboard').href='index.html';$('original').href='architecture.html';$('original').textContent='About the original viewer'; }")
 demo=demo.replace("$('logout').onclick=()=>{stop();", "$('logout').onclick=()=>{if(preview){location.href='index.html';return;}stop();")
 (DOCS/'demo.html').write_text(demo,encoding='utf-8')
 cards=''.join(f'<a class="card" href="{slug}.html"><h2>{escape(title)}</h2><p>{escape(sections[0][1][0][:170])}…</p></a>' for slug,title,sections in CHAPTERS)
 body='<div class="hero"><div><div class="eyebrow">LOCAL DIAGNOSTICS / ZEPKVOR ZEK-03</div><h1>Your board.<br>Your pins.<br>In view.</h1><p>A dedicated GPIO Viewer for Mzansi Connect. A photo-based ZEK-03 drawing, live pin inspection, an offline device page, and the original viewer kept alongside it.</p><div class="buttons"><a class="button primary" href="demo.html?demo=1">Explore the simulated demo</a><a class="button" href="Mzansi_GPIO_Viewer_ZEK03_Guide.pdf">Download the engineering guide</a></div><p>Viewer 1.0 · Mzansi firmware 2.2.6 · Android 1.3.0</p></div><img src="zek-03.svg" alt="Original ZEK-03 SVG, front view with OLED and USB-C down"></div><div class="callout"><strong>Evidence before assumptions.</strong><p>Physical header order follows the supplied photograph. OLED internal wiring remains unverified for ZEK-03. The hosted demo is simulated; real monitoring runs on the ESP32 over your local Wi-Fi.</p></div><h2>Learn, install, inspect</h2><div class="cards">'+cards+'</div>'
 (DOCS/'index.html').write_text(shell('GPIO Viewer for Mzansi Connect',body),encoding='utf-8')
 nav='<div class="sectionnav">'+''.join(f'<a href="{s}.html">{escape(t)}</a>' for s,t,_ in CHAPTERS)+'</div>'
 for slug,title,sections in CHAPTERS:
  body=f'<article><div class="eyebrow">ENGINEERING GUIDE / {slug.upper()}</div><h1>{escape(title)}</h1>'
  if slug=='hardware':
   body+='<img src="zek-03.svg" alt="ZEK-03 front view" style="max-height:430px;display:block;margin:auto"><table><tr><th>Position from top</th><th>Left</th><th>Right</th></tr>'+''.join(f'<tr><td>{i+1}</td><td>{l}</td><td>{r}</td></tr>' for i,(l,r) in enumerate(zip(['GPIO3','GPIO4','GPIO5','GPIO6','GPIO7','GPIO8','GPIO9','GPIO10'],['GPIO0','GPIO1','GPIO2','TX / GPIO21*','RX / GPIO20*','3V3','GND','5V'])))+'</table><p>* Numeric UART aliases use project test evidence, not a located Zepkvor schematic.</p>'
  for h,paragraphs in sections:body+='<h2>'+escape(h)+'</h2>'+''.join('<p>'+escape(p)+'</p>' for p in paragraphs)
  body+=nav+'</article>'; (DOCS/(slug+'.html')).write_text(shell(title,body),encoding='utf-8')
 refs='<article><h1>Sources and verification</h1><p>Checked for this release on 18 November 2026. Links are primary project, platform or maintainer sources; similar-board reports are identified explicitly.</p>'
 for i,(title,url,note) in enumerate(REFERENCES,1):refs+=f'<h2>R{i:02d} · {escape(title)}</h2><p>{escape(note)}</p><p><a href="{escape(url)}">Read the source</a></p>'
 verification=json.loads((ROOT/'verification.json').read_text(encoding='utf-8')) if (ROOT/'verification.json').exists() else {'Release verification':'In progress. Build and hardware results will be added after execution.'}
 refs+='<h2>Release evidence</h2>'+''.join(f'<h3>{escape(k)}</h3><p>{escape(str(v))}</p>' for k,v in verification.items())+nav+'</article>'
 (DOCS/'verification.html').write_text(shell('Sources and verification',refs),encoding='utf-8')
 (DOCS/'guide-content.json').write_text(json.dumps(CHAPTERS,indent=2),encoding='utf-8')

def build_pdf():
 from reportlab.platypus import BaseDocTemplate,PageTemplate,Frame,Paragraph,Spacer,PageBreak,Table,TableStyle,Image,NextPageTemplate,KeepTogether
 from reportlab.platypus.tableofcontents import TableOfContents
 from reportlab.lib.styles import ParagraphStyle
 from reportlab.lib.colors import HexColor,white
 from reportlab.lib.pagesizes import A4
 from reportlab.pdfbase import pdfmetrics
 from reportlab.pdfbase.ttfonts import TTFont
 from PIL import Image as PILImage
 fonts=Path('C:/Windows/Fonts')
 for name,file in [('Body','segoeui.ttf'),('Bold','segoeuib.ttf')]:pdfmetrics.registerFont(TTFont(name,str(fonts/file)))
 pdfmetrics.registerFontFamily('Body',normal='Body',bold='Bold',italic='Body',boldItalic='Bold')
 W,H=A4;M=48;CW=W-2*M;navy=HexColor('#102b3a');teal=HexColor('#007f79');ink=HexColor('#193540');muted=HexColor('#526976')
 body=ParagraphStyle('body',fontName='Body',fontSize=10.2,leading=15.5,textColor=ink,spaceAfter=11,allowWidows=0,allowOrphans=0)
 h1=ParagraphStyle('h1',fontName='Bold',fontSize=24,leading=29,textColor=navy,spaceAfter=17,keepWithNext=True)
 h2=ParagraphStyle('h2',fontName='Bold',fontSize=14,leading=19,textColor=teal,spaceBefore=12,spaceAfter=8,keepWithNext=True)
 small=ParagraphStyle('small',parent=body,fontSize=8.5,leading=12,textColor=muted)
 def P(t,style=body):return Paragraph(escape(t),style)
 def cover(c,d):
  c.setFillColor(navy);c.rect(0,0,W,H,fill=1,stroke=0)
  c.setStrokeColor(HexColor('#224353'))
  for x in range(0,int(W),24):c.line(x,0,x,H)
  for y in range(0,int(H),24):c.line(0,y,W,y)
  c.setFillColor(HexColor('#62dfcd'));c.setFont('Bold',10);c.drawString(M,H-65,'MZANSI CONNECT / ENGINEERING GUIDE')
  c.setFillColor(white);c.setFont('Bold',35)
  for i,line in enumerate(['GPIO VIEWER','FOR MZANSI','CONNECT']):c.drawString(M,H-133-i*43,line)
  c.setFont('Body',16);c.drawString(M,H-280,'Zepkvor ZEK-03 / ESP32-C3 OLED')
  c.setFont('Body',11);c.drawString(M,H-310,'Board support, installation, architecture and evidence')
  board=DOCS/'board-reference.png'
  if board.exists():c.drawImage(str(board),M+115,125,width=270,height=236,mask='auto',preserveAspectRatio=True,anchor='c')
  c.setFillColor(HexColor('#b9d3df'));c.setFont('Body',10);c.drawString(M,95,'Viewer 1.0.0  |  Firmware 2.2.6  |  Android 1.3.0')
  c.drawString(M,76,'18 November 2026 / Release engineering reference')
  c.setFont('Body',8);c.drawString(M,43,'Original viewer retained / OLED internals explicitly marked unverified')
 class Doc(BaseDocTemplate):
  def __init__(self,path):
   super().__init__(str(path),pagesize=A4,title='GPIO Viewer for Mzansi Connect - ZEK-03 Engineering Guide',author='Mzansi Connect',leftMargin=M,rightMargin=M,topMargin=65,bottomMargin=48)
   self.addPageTemplates([PageTemplate(id='cover',frames=[Frame(M,48,CW,H-110)],onPage=cover),PageTemplate(id='body',frames=[Frame(M,48,CW,H-110,leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)],onPageEnd=self.decorate)])
  def beforeDocument(self):self.current='CONTENTS'
  def afterFlowable(self,f):
   if hasattr(f,'key'):
    self.current=f.label;self.canv.bookmarkPage(f.key);self.canv.addOutlineEntry(f.label,f.key,0);self.notify('TOCEntry',(0,f.label,self.page,f.key))
  def decorate(self,c,d):
   c.setStrokeColor(HexColor('#cbdade'));c.line(M,H-38,W-M,H-38);c.line(M,36,W-M,36)
   c.setFillColor(teal);c.setFont('Bold',8);c.drawString(M,H-28,'MZANSI CONNECT / ZEK-03 GPIO VIEWER')
   c.setFillColor(muted);c.setFont('Body',7.6);c.drawRightString(W-M,H-28,self.current[:45]);c.drawString(M,23,'Engineering guide / 18 November 2026');c.drawRightString(W-M,23,str(d.page))
 story=[Spacer(1,640),NextPageTemplate('body'),PageBreak(),P('Contents',h1),P('A project-specific guide to the added viewer, its physical board model, safe operation and verification. Page links and PDF bookmarks are generated from the final document.',body)]
 toc=TableOfContents();toc.levelStyles=[ParagraphStyle('toc',parent=body,fontSize=10.5,leading=17,spaceBefore=3)];toc.dotsMinLevel=0;story.append(toc)
 for n,(slug,title,sections) in enumerate(CHAPTERS,1):
  story.append(PageBreak());q=P(f'{n:02d}  {title}',h1);q.key=slug;q.label=f'{n:02d} {title}';story.append(q)
  if slug=='hardware':
   rows=[['Position','Left header','Right header']]+[[str(i+1),l,r] for i,(l,r) in enumerate(zip(['GPIO3','GPIO4','GPIO5','GPIO6','GPIO7','GPIO8','GPIO9','GPIO10'],['GPIO0','GPIO1','GPIO2','TX / GPIO21*','RX / GPIO20*','3V3','GND','5V']))]
   cells=[[P(x,small) for x in row] for row in rows];t=Table(cells,colWidths=[CW*.2,CW*.4,CW*.4],repeatRows=1);t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#d9e9eb')),('ROWBACKGROUNDS',(0,1),(-1,-1),[white,HexColor('#f0f5f6')]),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]));story.extend([t,Spacer(1,10),P('* UART aliases are supported by project wiring/test evidence; a manufacturer schematic remains unavailable.',small)])
  for heading,paragraphs in sections:
   story.append(P(heading,h2))
   for text in paragraphs:story.append(P(text))
  if slug=='overview' and (DOCS/'viewer-desktop.png').exists():
   story.extend([PageBreak(),P('The interface at a glance',h2),Image(str(DOCS/'viewer-desktop.png'),width=CW,height=CW*700/1440),P('Browser fixture illustration. TEST-DEVICE and the shown HIGH/LOW values are simulated; they are not presented as readings from the connected board.',small)])
 for label,title in [('references','Sources and educational reading'),('verification','Release verification')]:
  story.append(PageBreak());q=P(title,h1);q.key=label;q.label=title;story.append(q)
  if label=='references':
   for i,(title,url,note) in enumerate(REFERENCES,1):
    story.append(P(f'R{i:02d} / {title}',h2));story.append(P(note));story.append(Paragraph('<link href="'+escape(url)+'" color="#007f79">'+escape(url)+'</link>',small))
   story.append(P('Additional project evidence',h2));story.append(P('The user-supplied product image establishes external physical order. Current firmware source, its bridge, the Android mode changes and the recorded GPS UART test establish implementation behavior. The image itself is not redistributed in the public repository.'))
  else:
   evidence=json.loads((ROOT/'verification.json').read_text(encoding='utf-8')) if (ROOT/'verification.json').exists() else {'Status':'Verification is still in progress.'}
   for key,value in evidence.items():story.extend([P(key,h2),P(str(value))])
   story.append(P('Decision before retiring the original',h2));story.append(P('Compare both viewers on your actual board and phone over several normal sessions. Keep the original until physical pin mapping, reconnect behavior, startup reliability and the important operator workflows meet your needs. This release leaves that choice with the operator.'))
 out=DOCS/'Mzansi_GPIO_Viewer_ZEK03_Guide.pdf';Doc(out).multiBuild(story)
 dest=ROOT.parent/'output/pdf'
 if (ROOT.parent/'Mzansi_GPS_NRF_C3').is_dir():dest.mkdir(parents=True,exist_ok=True);shutil.copy2(out,dest/out.name)
 print('PDF:',out)

if __name__=='__main__':
 build_site()
 import sys
 if '--pdf' in sys.argv:build_pdf()
 print('Website:',DOCS/'index.html')
