import json
import re

with open('route_mobiles.json', 'r', encoding='utf-8') as f:
    rms = json.load(f)

for rm in rms:
    off = rm['officer'].replace('\n', ' ')
    # Match rank/station like SI/Hiramandalam or SI - Patapatnam
    m = re.search(r'\b(SDPO|Addl\.?\s*SP|DSP|CI|Inspector|IOP|WCI|SI|WSI|Sub Inspector|ASI|WASI|HC|WHC|PC|WPC)\s*[\/\-]\s*([A-Za-z0-9\s\.\(\)\&]+?)(?:\s*(?:Ph\.?)?[6-9]\d{9}|\s*[\r\n,;]|$)', off, re.I)
    if m:
        rank = m.group(1).strip()
        ps = m.group(2).strip()
        print(f"{rm['id']}: '{off}' ==> {rank}, {ps}")
