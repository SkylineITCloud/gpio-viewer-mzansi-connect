"""Check the photo-authoritative header order and generated asset consistency."""
from pathlib import Path
import json,gzip,re,xml.etree.ElementTree as ET
root=Path(__file__).resolve().parents[1]
b=json.loads((root/'web/board.json').read_text(encoding='utf-8'))
assert [p['label'] for p in b['pins'] if p['side']=='left']==['3','4','5','6','7','8','9','10']
assert [p['label'] for p in b['pins'] if p['side']=='right']==['0','1','2','TX','RX','3V3','GND','5V']
assert len(b['pins'])==16 and len({p['id'] for p in b['pins']})==16
assert len([p for p in b['pins'] if p['gpio'] is not None])==13
assert all(p['gpio'] is None for p in b['pins'] if p['kind']!='gpio')
assert [p['gpio'] for p in b['pins'] if p['label'] in ['TX','RX']]==[21,20]
assert all(b['oled'][f] is None for f in ['controller','resolution','sda','scl','address','sharedHeaderPins'])
ET.fromstring((root/'web/zek-03.svg').read_text(encoding='utf-8'))
header=(root/'integration/mzansi_gpio_html.h').read_text(encoding='utf-8')
payload=bytes(int(x,16) for x in re.findall(r'0x([0-9a-f]{2})',header))
assert gzip.decompress(payload)==(root/'web/index.html').read_bytes()
assert b['pins'][7]['y']==b['pins'][15]['y']
print('PASS: exact header order, supply/GPIO separation, unknown OLED metadata, SVG and gzip asset')
