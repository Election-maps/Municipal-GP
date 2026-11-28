import openpyxl
import json
import re

excel_path = r"C:\Users\SKL-ITCORE2\Desktop\Phase-2\2. Force - GP Election Phase-2-2026 on 28-11-2026.xlsx"
wb = openpyxl.load_workbook(excel_path, data_only=True)

def clean(v):
    return str(v).strip() if v is not None else ""

def extract_phone(text):
    if not text:
        return ""
    m = re.findall(r'[6-9]\d{9}', str(text))
    if m:
        return m[0]
    return ""

units = []

# 1. Routes (Sheet 'Routes') - exactly 128 routes
ws_routes = wb["Routes"]
for r in range(2, 130):
    sno = clean(ws_routes.cell(r, 1).value)
    mandal = clean(ws_routes.cell(r, 2).value)
    r_no = clean(ws_routes.cell(r, 3).value)
    incharge = clean(ws_routes.cell(r, 4).value)
    supp = clean(ws_routes.cell(r, 5).value)
    hq = clean(ws_routes.cell(r, 6).value)
    
    if not sno and not r_no:
        continue
        
    r_num_str = str(r_no).replace("Route -", "").replace("Route-", "").replace("Route", "").strip()
    route_num = f"Route-{r_num_str}"
    uid = f"RM_{mandal}_{route_num}_{sno}".replace(" ", "_")
    phone = extract_phone(incharge) or extract_phone(supp)
    
    units.append({
        "id": uid,
        "category": "Route Mobiles",
        "categoryKey": "RM",
        "mandal": mandal,
        "route": route_num,
        "unitName": f"{route_num} ({hq})",
        "hq": hq,
        "officer": incharge.replace("\n", ", "),
        "phone": phone,
        "supporting": supp.replace("\n", ", "),
        "pollingStations": f"Head Quarter: {hq}"
    })

print(f"Routes extracted: {len(units)}")

# 2. Striking Forces (Sheet 'Striking Forces') - exactly 30 SFs
ws_sf = wb["Striking Forces"]
sf_count = 0
for r in range(4, 34):
    sno = clean(ws_sf.cell(r, 1).value)
    gp = clean(ws_sf.cell(r, 2).value)
    mandal = clean(ws_sf.cell(r, 3).value)
    sf_no = clean(ws_sf.cell(r, 4).value)
    hq = clean(ws_sf.cell(r, 5).value)
    officer = clean(ws_sf.cell(r, 6).value)
    supp = clean(ws_sf.cell(r, 7).value)
    
    if not sno and not mandal and not officer:
        continue
        
    phone = extract_phone(officer) or extract_phone(supp)
    sf_count += 1
    uid = f"SF_{mandal}_{sf_no}_{sno}".replace(" ", "_")
    units.append({
        "id": uid,
        "category": "Striking Forces",
        "categoryKey": "SF",
        "mandal": mandal,
        "route": f"SF-{sf_no}",
        "unitName": f"SF-{sf_no} ({gp})",
        "hq": hq,
        "officer": officer.replace("\n", ", "),
        "phone": phone,
        "supporting": supp.replace("\n", ", "),
        "pollingStations": f"GP: {gp}, HQ: {hq}"
    })

print(f"SF extracted: {sf_count}")

# 3. Special Striking Forces (Sheet 'Special Striking Forces') - exactly 26 SSFs
ws_ssf = wb["Special Striking Forces"]
ssf_count = 0
for r in range(4, 30):
    sno = clean(ws_ssf.cell(r, 1).value)
    gp = clean(ws_ssf.cell(r, 2).value)
    mandal = clean(ws_ssf.cell(r, 3).value)
    ssf_no = clean(ws_ssf.cell(r, 4).value)
    hq = clean(ws_ssf.cell(r, 5).value)
    officer = clean(ws_ssf.cell(r, 6).value)
    supp = clean(ws_ssf.cell(r, 7).value)
    
    if not sno and not mandal and not officer:
        continue
        
    phone = extract_phone(officer) or extract_phone(supp)
    ssf_count += 1
    uid = f"SSF_{mandal}_{ssf_no}_{sno}".replace(" ", "_")
    units.append({
        "id": uid,
        "category": "Special Striking Forces",
        "categoryKey": "SSF",
        "mandal": mandal,
        "route": f"SSF-{ssf_no}",
        "unitName": f"SSF-{ssf_no} ({gp})",
        "hq": hq,
        "officer": officer.replace("\n", ", "),
        "phone": phone,
        "supporting": supp.replace("\n", ", "),
        "pollingStations": f"GP: {gp}, HQ: {hq}"
    })

print(f"SSF extracted: {ssf_count}")

# 4. QRTs (Sheet 'QRTss' - exactly 5 QRT teams: QRT-1 to QRT-5)
ws_qrt = wb["QRTss"]
qrt_count = 0
for r in range(3, 8):
    sno = clean(ws_qrt.cell(r, 1).value)
    name = clean(ws_qrt.cell(r, 2).value)
    loc = clean(ws_qrt.cell(r, 3).value)
    officer = clean(ws_qrt.cell(r, 4).value)
    
    if not sno and not name and not officer:
        continue
        
    phone = extract_phone(officer)
    mandal_name = loc.split(",")[0].replace("Mandals", "").replace("Mandal", "").strip() if loc else "Srikakulam"
    qrt_count += 1
    uid = f"QRT_{sno}_{name}".replace(" ", "_").replace("-", "_")
    units.append({
        "id": uid,
        "category": "QRTs",
        "categoryKey": "QRT",
        "mandal": mandal_name,
        "route": name,
        "unitName": f"{name} ({loc})",
        "hq": loc,
        "officer": officer.replace("\n", ", "),
        "phone": phone,
        "supporting": officer.replace("\n", ", "),
        "pollingStations": loc
    })

print(f"QRT extracted (strictly 5 QRT teams): {qrt_count}")

# 5. Reserve Parties (Sheet 'Addl. SP Reserve' - exactly 2 Reserve teams)
ws_asp = wb["Addl. SP Reserve"]
asp_count = 0
for r in range(2, 4):
    sno = clean(ws_asp.cell(r, 1).value)
    force_type = clean(ws_asp.cell(r, 2).value)
    area = clean(ws_asp.cell(r, 3).value)
    officer = clean(ws_asp.cell(r, 4).value)
    remarks = clean(ws_asp.cell(r, 5).value)
    
    if not sno and not officer:
        continue
        
    phone = extract_phone(officer)
    asp_count += 1
    uid = f"Addl_SP_Reserve_{sno}"
    clean_area = area.replace("\n", " ").strip()
    units.append({
        "id": uid,
        "category": "Reserve Parties",
        "categoryKey": "RESERVE",
        "mandal": clean_area,
        "route": f"Addl. SP Reserve - {sno}",
        "unitName": f"Addl. SP Reserve - {clean_area}",
        "hq": clean_area,
        "officer": officer.replace("\n", ", "),
        "phone": phone,
        "supporting": remarks or officer.replace("\n", ", "),
        "pollingStations": clean_area
    })

print(f"Reserve Parties extracted (strictly 2 Reserve teams): {asp_count}")

# 6. Static Parties (Sheet 'Statck' - exactly 27 static parties)
ws_statck = wb["Statck"]
statck_count = 0
for r in range(3, ws_statck.max_row + 1):
    mandal = clean(ws_statck.cell(r, 1).value)
    gp = clean(ws_statck.cell(r, 2).value)
    ps = clean(ws_statck.cell(r, 3).value)
    psl = clean(ws_statck.cell(r, 4).value)
    officer = clean(ws_statck.cell(r, 5).value)
    
    if not mandal and not ps and not officer:
        continue
        
    phone = extract_phone(officer)
    statck_count += 1
    uid = f"Static_{statck_count}"
    units.append({
        "id": uid,
        "category": "Static Parties",
        "categoryKey": "STATIC",
        "mandal": mandal,
        "route": f"Static-{statck_count}",
        "unitName": f"Static-{statck_count} ({psl})",
        "hq": gp,
        "officer": officer.replace("\n", ", "),
        "phone": phone,
        "supporting": officer.replace("\n", ", "),
        "pollingStations": f"PSL: {psl}, PS: {ps}, GP: {gp}"
    })

print(f"Static Party extracted: {statck_count}")
print(f"Total units extracted: {len(units)}")

# Write to route_mobiles.json
with open(r"c:\Users\SKL-ITCORE2\Desktop\Municipal-GP\route_mobiles.json", "w", encoding="utf-8") as f:
    json.dump(units, f, indent=2, ensure_ascii=False)

# Write to route_mobiles_data.js
js_content = "window.ROUTE_MOBILES_DATA = " + json.dumps(units, indent=2, ensure_ascii=False) + ";\n"
with open(r"c:\Users\SKL-ITCORE2\Desktop\Municipal-GP\route_mobiles_data.js", "w", encoding="utf-8") as f:
    f.write(js_content)

print("Successfully written route_mobiles.json and route_mobiles_data.js!")
