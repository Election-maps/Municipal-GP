import json
import math
import time
import urllib.request
import re

ROMAN_MAP = {
    '1': 'I', '2': 'II', '3': 'III', '4': 'IV', '5': 'V',
    '6': 'VI', '7': 'VII', '8': 'VIII', '9': 'IX', '10': 'X',
    '11': 'XI', '12': 'XII', '13': 'XIII', '14': 'XIV', '15': 'XV',
    '16': 'XVI', '17': 'XVII', '18': 'XVIII', '19': 'XIX', '20': 'XX'
}
REV_ROMAN_MAP = {v: k for k, v in ROMAN_MAP.items()}

def haversine_dist(p1, p2):
    lat1, lon1 = math.radians(p1[0]), math.radians(p1[1])
    lat2, lon2 = math.radians(p2[0]), math.radians(p2[1])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))
    return 6371.0 * c  # km

def solve_tsp_nearest_neighbor(points):
    """Sort points into a natural sequential patrol order to prevent zig-zags."""
    if len(points) <= 2:
        return points
    
    unvisited = points[1:]
    ordered = [points[0]]
    curr = points[0]
    
    while unvisited:
        nearest_idx = 0
        min_d = haversine_dist(curr, unvisited[0])
        for idx in range(1, len(unvisited)):
            d = haversine_dist(curr, unvisited[idx])
            if d < min_d:
                min_d = d
                nearest_idx = idx
        curr = unvisited.pop(nearest_idx)
        ordered.append(curr)
        
    return ordered

def fetch_osrm_geometry(points):
    """Fetch true driving road polyline from OSRM for ordered points."""
    # points: list of (lat, lng)
    pts_str = ';'.join(f"{lng:.6f},{lat:.6f}" for lat, lng in points)
    url = f"http://router.project-osrm.org/route/v1/driving/{pts_str}?overview=full&geometries=geojson"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'ElectionMapPatrolGen/2.0'})
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if data.get('code') == 'Ok' and data.get('routes'):
                route = data['routes'][0]
                dist_km = round(route['distance'] / 1000.0, 1)
                # Convert [lng, lat] to [lat, lng]
                leaflet_coords = [[round(c[1], 5), round(c[0], 5)] for c in route['geometry']['coordinates']]
                return dist_km, leaflet_coords
    except Exception as e:
        print(f"    [WARN] OSRM error: {e}")
        
    return None, None

def generate_local_stub(point):
    """For single-station routes, generate a short 150m patrol segment along the road."""
    lat, lng = point
    delta = 0.001
    return 0.3, [
        [round(lat - delta, 5), round(lng, 5)],
        [round(lat, 5), round(lng, 5)],
        [round(lat + delta, 5), round(lng, 5)]
    ]

def main():
    print("Loading data/stations.json...")
    with open('data/stations.json', 'r', encoding='utf-8') as f:
        stations = json.load(f)
        
    # Load existing routes_geometry.js if present to preserve legacy routes
    existing_routes = {}
    try:
        with open('data/routes_geometry.js', 'r', encoding='utf-8') as f:
            content = f.read()
            # Match JSON inside window.PRECOMPUTED_ROUTES = { ... };
            m = re.search(r'window\.PRECOMPUTED_ROUTES\s*=\s*(\{.*\});?', content, re.DOTALL)
            if m:
                existing_routes = json.loads(m.group(1))
                print(f"Loaded {len(existing_routes)} existing legacy routes from data/routes_geometry.js")
    except Exception as e:
        print(f"Could not load legacy routes: {e}")

    # Group stations by unique route identification
    # Group key: (mandal, psname, route_no)
    route_groups = {}
    for s in stations:
        mandal = (s.get('mandal_zptc_segment') or '').strip()
        ps = (s.get('psname') or mandal or '').strip()
        r = str(s.get('route_no') or '').strip()
        if not r:
            continue
            
        lat = float(s.get('latitude') or 0)
        lng = float(s.get('longitude') or 0)
        if lat == 0 or lng == 0:
            continue
            
        key = (mandal, ps, r)
        if key not in route_groups:
            route_groups[key] = {
                'mandal': mandal,
                'ps': ps,
                'route': r,
                'points': [],
                'stations': []
            }
        route_groups[key]['points'].append((lat, lng))
        route_groups[key]['stations'].append(s.get('polling_station_location'))

    print(f"Found {len(route_groups)} distinct route groups to process.")
    
    new_computed = {}
    success_count = 0
    fallback_count = 0

    for idx, (grp_key, grp_data) in enumerate(route_groups.items(), 1):
        mandal, ps, r = grp_key
        raw_pts = grp_data['points']
        
        # Deduplicate consecutive/identical points
        pts = []
        for p in raw_pts:
            if not pts or (abs(pts[-1][0] - p[0]) > 0.0001 or abs(pts[-1][1] - p[1]) > 0.0001):
                pts.append((round(p[0], 6), round(p[1], 6)))
                
        print(f"[{idx}/{len(route_groups)}] Computing route for {ps} (Mandal: {mandal}) - Route {r} ({len(pts)} distinct stations)...")
        
        road_coords = None
        dist_km = 0.0
        
        if len(pts) >= 2:
            ordered_pts = solve_tsp_nearest_neighbor(pts)
            dist_km, road_coords = fetch_osrm_geometry(ordered_pts)
            time.sleep(0.12)  # Polite pause between OSRM calls
            
        if not road_coords or len(road_coords) < 2:
            if len(pts) >= 2:
                print("    Using fallback straight/spline road connect...")
                ordered_pts = solve_tsp_nearest_neighbor(pts)
                road_coords = [[round(p[0], 5), round(p[1], 5)] for p in ordered_pts]
                dist_km = round(sum(haversine_dist(road_coords[i], road_coords[i+1]) for i in range(len(road_coords)-1)), 1)
                fallback_count += 1
            else:
                dist_km, road_coords = generate_local_stub(pts[0])
                fallback_count += 1
        else:
            success_count += 1
            print(f"    OK: {dist_km} km, {len(road_coords)} road waypoints")

        route_payload = {
            "distKm": dist_km,
            "coordinates": road_coords
        }

        # Generate ALL alias keys to guarantee lookup success under any user/code filter
        roman_r = ROMAN_MAP.get(r, r)
        
        # 1. Primary psname keys
        primary_key = f"{ps}_{r}"
        new_computed[primary_key] = route_payload
        new_computed[f"{ps}_{roman_r}"] = route_payload
        
        # 2. Mandal keys (e.g., Palasa_1, Sompeta_1, Ichapuram_1)
        if mandal and mandal != ps:
            new_computed[f"{mandal}_{r}"] = route_payload
            new_computed[f"{mandal}_{roman_r}"] = route_payload

        # 3. Clean PS names (stripping 'PS', 'ps', 'Rural', etc.)
        ps_stripped = re.sub(r'(?i)\b(ps|rural|town)\b', '', ps).strip()
        if ps_stripped:
            ps_clean = re.sub(r'\s+', ' ', ps_stripped)
            new_computed[f"{ps_clean}_{r}"] = route_payload
            new_computed[f"{ps_clean}_{roman_r}"] = route_payload
            
        # 4. Standard case variations
        new_computed[f"{ps.upper()}_{r}"] = route_payload
        new_computed[f"{ps.lower()}_{r}"] = route_payload
        if mandal:
            new_computed[f"{mandal.upper()}_{r}"] = route_payload
            new_computed[f"{mandal.lower()}_{r}"] = route_payload

    print(f"\nCompleted road route computation:")
    print(f"  OSRM Road Routes: {success_count}")
    print(f"  Single station / Local stubs: {fallback_count}")
    print(f"  Total generated alias keys: {len(new_computed)}")
    
    # Merge existing legacy routes with newly computed routes (newly computed overrides)
    merged_routes = {}
    merged_routes.update(existing_routes)
    merged_routes.update(new_computed)
    print(f"Total merged routes in database: {len(merged_routes)}")
    
    # Save to data/routes_geometry.json
    print("Writing data/routes_geometry.json...")
    with open('data/routes_geometry.json', 'w', encoding='utf-8') as f:
        json.dump(merged_routes, f, indent=2, ensure_ascii=False)
        
    # Save to data/routes_geometry.js
    print("Writing data/routes_geometry.js...")
    js_content = "window.PRECOMPUTED_ROUTES=" + json.dumps(merged_routes, separators=(',', ':'), ensure_ascii=False) + ";\n"
    with open('data/routes_geometry.js', 'w', encoding='utf-8') as f:
        f.write(js_content)
        
    print("SUCCESS: data/routes_geometry.js and data/routes_geometry.json generated successfully!")

if __name__ == '__main__':
    main()
