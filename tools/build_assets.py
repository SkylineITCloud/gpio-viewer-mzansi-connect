"""Build the offline viewer, board SVG, upstream-compatible profile and flash asset."""
from pathlib import Path
import gzip
import json

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / 'web'
pins = []
for side, labels in [('left', ['3','4','5','6','7','8','9','10']), ('right', ['0','1','2','TX','RX','3V3','GND','5V'])]:
    for i, label in enumerate(labels):
        gpio = int(label) if label.isdigit() and label != '5V' else {'TX':21,'RX':20}.get(label)
        pins.append(dict(id=f'{side}-{i+1}', side=side, position=i+1, label=label, gpio=gpio,
                         kind='gpio' if gpio is not None else 'ground' if label=='GND' else 'power',
                         x=156 if side=='left' else 404, y=128+i*34))
board = dict(id='zepkvor-zek-03', name='Zepkvor ZEK-03 · ESP32-C3 OLED', orientation='Front; USB-C down',
             pins=pins, oled=dict(controller=None,resolution=None,sda=None,scl=None,address=None,sharedHeaderPins=None,verification='Unverified on ZEK-03'),
             uartEvidence='TX=GPIO21 / RX=GPIO20: project UART wiring and recorded NMEA test; no Zepkvor schematic found.',
             imageEvidence='User-supplied product photo, 17 November 2026; physical order confirmed visually. Dimensions are illustrative, not a manufacturing drawing.')
(WEB/'board.json').write_text(json.dumps(board,indent=2)+'\n',encoding='utf-8',newline='\n')
svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 560 490" role="img" aria-labelledby="boardTitle boardDesc">',
 '<title id="boardTitle">Zepkvor ZEK-03 front view</title><desc id="boardDesc">Purple board, reset and boot at top, OLED in centre, USB-C at bottom, eight pins per side.</desc>',
 '<defs><linearGradient id="pcb" x2="1" y2="1"><stop stop-color="#61357c"/><stop offset="1" stop-color="#301846"/></linearGradient><linearGradient id="metal" x2="1" y2="1"><stop stop-color="#f5f4eb"/><stop offset=".45" stop-color="#919da8"/><stop offset="1" stop-color="#d9e0e4"/></linearGradient></defs>',
 '<rect x="140" y="56" width="280" height="344" rx="14" fill="url(#pcb)" stroke="#9c70af" stroke-width="2"/>',
 '<g fill="#d2d5d7" stroke="#818b95"><rect x="159" y="62" width="64" height="36" rx="4"/><rect x="337" y="62" width="64" height="36" rx="4"/></g>',
 '<g fill="#69717b" stroke="#3a414a" stroke-width="2"><circle cx="191" cy="80" r="12"/><circle cx="369" cy="80" r="12"/></g>',
 '<rect x="254" y="65" width="48" height="28" rx="3" fill="#ddd"/><rect x="260" y="69" width="36" height="20" fill="#c12638"/><rect x="272" y="75" width="12" height="7" fill="#efc2b8"/>',
 '<g font-family="system-ui,sans-serif" fill="#e4d9eb" font-size="12"><text x="230" y="92" transform="rotate(-90 230 92)">RST</text><text x="330" y="94" transform="rotate(-90 330 94)">BOOT</text></g>']
for i in range(10):
    x=190+i*18
    svg.append(f'<rect x="{x}" y="112" width="10" height="17" rx="2" fill="#bbb7a5"/><rect x="{x+2}" y="116" width="6" height="9" fill="#3b3a40"/>')
svg += ['<rect x="193" y="137" width="174" height="170" fill="#aaa9a5" stroke="#d5d2d0" stroke-width="3"/>',
 '<rect x="201" y="145" width="158" height="103" fill="#1c1b26"/><rect x="208" y="152" width="144" height="90" fill="#302345"/><rect x="209" y="249" width="142" height="48" fill="#7b7d79"/>',
 '<path d="M210 299 L230 299 L237 321 L218 321Z M328 299 L348 299 L340 321 L321 321Z" fill="#bd8d3e"/><rect x="232" y="308" width="90" height="24" fill="#171c25"/>',
 '<g fill="#c7cdd2"><rect x="211" y="327" width="138" height="42" rx="6"/><rect x="219" y="338" width="122" height="88" rx="7" fill="url(#metal)" stroke="#6c7783" stroke-width="3"/><rect x="231" y="405" width="98" height="13" rx="5" fill="#27323b"/></g>',
 '<rect x="184" y="347" width="9" height="24" rx="2" fill="#dae8d2"/><rect x="367" y="347" width="9" height="24" rx="2" fill="#dae8d2"/><text x="191" y="337" transform="rotate(-90 191 337)" fill="#eee0ef" font-size="10">PWR</text><text x="374" y="337" transform="rotate(-90 374 337)" fill="#eee0ef" font-size="10">IO8</text>',
 '<text x="280" y="463" text-anchor="middle" fill="#a5b1c3" font-size="13" font-family="system-ui">ZEK-03 · front · USB-C down</text>']
for pin in pins:
    x,y=pin['x'],pin['y']; gpio=pin['gpio']; label=pin['label']
    color='#cdb986' if pin['kind']=='gpio' else '#faaf70' if pin['kind']=='power' else '#9aabbf'
    svg.append(f'<g id="{pin["id"]}" class="pin {pin["kind"]}" data-pin="{pin["id"]}" tabindex="0" role="button" aria-label="{label}"><title>{label}: '+('programmable GPIO' if gpio is not None else 'supply rail; not a GPIO')+'</title>')
    svg.append(f'<rect x="{x-14}" y="{y-14}" width="28" height="28" fill="transparent" pointer-events="all"/>')
    if pin['position']==8: svg.append(f'<rect x="{x-10}" y="{y-10}" width="20" height="20" fill="{color}"/>')
    svg.append(f'<circle class="ring" cx="{x}" cy="{y}" r="9" fill="#171221" stroke="{color}" stroke-width="4"/><circle class="live" cx="{x}" cy="{y}" r="5" fill="#74657c"/>')
    tx=176 if pin['side']=='left' else 384
    svg.append(f'<text x="{tx}" y="{y+5}" text-anchor="'+('start' if pin['side']=='left' else 'end')+f'" fill="#eee0ef" font-family="system-ui" font-size="14">{label}</text>')
    sx=25 if pin['side']=='left' else 435
    svg.append(f'<text class="pin-state" x="{sx}" y="{y+4}" fill="#a5b1c3" font-family="system-ui" font-size="12">'+('—' if gpio is not None else label)+'</text></g>')
svg.append('</svg>')
(WEB/'zek-03.svg').write_text('\n'.join(svg),encoding='utf-8',newline='\n')
# Same registration/indicator schema as upstream, for an optional upstream contribution.
(ROOT/'boards.json').write_text(json.dumps([dict(name=board['name'],image='web/zek-03.svg',pins='zek-03-indicators.json')],indent=2)+'\n',encoding='utf-8',newline='\n')
(ROOT/'zek-03-indicators.json').write_text(json.dumps(dict(pins=[dict(gpioid=p['gpio'],top=100*p['y']/490,left=100*p['x']/560,valueJustify=-1 if p['side']=='left' else 0) for p in pins if p['gpio'] is not None],settings=dict(pinWidth=4,pinHeight=4,showPinNumber=True,valueMinWidth=25,valuePinMargin=4,valueFontSize=2)),indent=2)+'\n',encoding='utf-8',newline='\n')
html=(WEB/'template.html').read_text(encoding='utf-8').replace('<!--BOARD-->',(WEB/'zek-03.svg').read_text(encoding='utf-8')).replace('/*BOARD_DATA*/',json.dumps(board,separators=(',',':'))).replace('/*TELEMETRY*/',(WEB/'telemetry.js').read_text(encoding='utf-8'))
(WEB/'index.html').write_text(html,encoding='utf-8',newline='\n')
payload=gzip.compress(html.encode(),compresslevel=9,mtime=0)
header='// Generated by GPIOViewer_ZEK03/tools/build_assets.py. Do not hand edit.\n#pragma once\n#include <Arduino.h>\nstatic const uint8_t MZANSI_GPIO_HTML_GZ[] PROGMEM = {\n'
header+='\n'.join(','.join(f'0x{b:02x}' for b in payload[i:i+24])+',' for i in range(0,len(payload),24))+'\n};\n'
integration=ROOT/'integration'
integration.mkdir(exist_ok=True)
(integration/'mzansi_gpio_html.h').write_text(header,encoding='utf-8',newline='\n')
if (ROOT.parent/'Mzansi_GPS_NRF_C3').is_dir():
    (ROOT.parent/'Mzansi_GPS_NRF_C3/mzansi_gpio_html.h').write_text(header,encoding='utf-8',newline='\n')
print(f'Built offline viewer: {len(html.encode()):,} bytes; flash gzip: {len(payload):,} bytes')
