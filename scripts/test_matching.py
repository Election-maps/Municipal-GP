import json
import re

with open('data/routes_geometry.json', 'r', encoding='utf-8') as f:
    precomputed = json.load(f)

with open('data/stations.json', 'r', encoding='utf-8') as f:
    stations = json.load(f)

roman_map = {
    '1':'I', '2':'II', '3':'III', '4':'IV', '5':'V',
    '6':'VI', '7':'VII', '8':'VIII', '9':'IX', '10':'X',
    '11':'XI', '12':'XII', '13':'XIII', '14':'XIV', '15':'XV',
    '16':'XVI', '17':'XVII', '18':'XVIII', '19':'XIX'
}

missing = set()
found = set()

for s in stations:
    ps = (s.get('psname') or '').strip()
    r = str(s.get('route_no') or '').strip()
    m = (s.get('mandal_zptc_segment') or '').strip()
    if not r:
        continue

    clean_p = re.sub(r'(?i)\b(ps|rural|town)\b', '', ps).strip()
    clean_m = re.sub(r'(?i)\b(ps|rural|town)\b', '', m).strip()
    cands = [
        f"{ps}_{r}",
        f"{ps}_{roman_map.get(r, '')}",
        f"{m}_{r}",
        f"{m}_{roman_map.get(r, '')}",
        f"{clean_p}_{r}",
        f"{clean_m}_{r}"
    ]
    matched = any(c in precomputed and precomputed[c].get('coordinates') for c in cands if c)
    if matched:
        found.add(f"{ps}_{r}")
    else:
        missing.add(f"{ps}_{r} (Mandal: {m})")

print(f"Total distinct routes in stations: {len(found) + len(missing)}")
print(f"Routes found in PRECOMPUTED_ROUTES: {len(found)}")
print(f"Missing routes: {len(missing)}")
if missing:
    print("Missing list:", missing)
