import json

with open('data/stations.json', 'r', encoding='utf-8') as f:
    stations = json.load(f)

by_ps = {}
no_route_stations = []

for s in stations:
    ps = (s.get('psname') or '').strip()
    r = str(s.get('route_no') or '').strip()
    m = (s.get('mandal_zptc_segment') or '').strip()
    lat = float(s.get('latitude') or 0)
    lng = float(s.get('longitude') or 0)
    if not r:
        no_route_stations.append(s)
        continue
    k = f'{ps}_{r}'
    if k not in by_ps:
        by_ps[k] = {'ps': ps, 'mandal': m, 'route': r, 'stations': []}
    by_ps[k]['stations'].append({
        'sno': s.get('sno'),
        'name': s.get('polling_station_location'),
        'lat': lat,
        'lng': lng
    })

print(f"Total stations: {len(stations)}")
print(f"Stations without route_no: {len(no_route_stations)}")
print(f"Total distinct routes: {len(by_ps)}")
print("\nBreakdown by PS:")
ps_summary = {}
for k, v in by_ps.items():
    ps = v['ps']
    ps_summary[ps] = ps_summary.get(ps, 0) + 1

for ps, count in sorted(ps_summary.items()):
    routes = [v['route'] for v in by_ps.values() if v['ps'] == ps]
    print(f"  {ps}: {count} routes -> {routes}")
