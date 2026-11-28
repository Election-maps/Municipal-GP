import openpyxl
import json
import re
import datetime
import os

def clean_str(val):
    if val is None:
        return ""
    return str(val).strip()

def extract_phone(val):
    if not val:
        return ""
    s = str(val)
    m = re.findall(r'\b[6-9]\d{9}\b', s)
    if m:
        return m[0]
    m2 = re.findall(r'\d{10}', s)
    if m2:
        return m2[0]
    return ""

def run_conversion():
    wb1_path = r'C:\Users\SKL-ITCORE2\Desktop\Phase-2\1. GP Election Phase-2-2026 on 28-11-2026.xlsx'
    wb2_path = r'C:\Users\SKL-ITCORE2\Desktop\Phase-2\2. Force - GP Election Phase-2-2026 on 28-11-2026.xlsx'

    print("=============================================================")
    print("STEP 1: Reading 2. Force Excel for Updated Route & Forces Map")
    print("=============================================================")
    wb2 = openpyxl.load_workbook(wb2_path, data_only=True)

    # 1. Routes map: (mandal.lower(), route_no) -> (incharge, supporting, hq)
    ws_routes = wb2['Routes']
    routes_map = {}
    for r in range(2, ws_routes.max_row + 1):
        mandal = clean_str(ws_routes.cell(r, 2).value)
        route_no = clean_str(ws_routes.cell(r, 3).value)
        if mandal and route_no:
            incharge = clean_str(ws_routes.cell(r, 4).value)
            supp = clean_str(ws_routes.cell(r, 5).value)
            hq = clean_str(ws_routes.cell(r, 6).value)
            routes_map[(mandal.lower(), route_no)] = {
                'incharge': incharge,
                'supporting': supp,
                'hq': hq
            }
    print(f"Loaded {len(routes_map)} routes from 2. Force sheet 'Routes'")

    # 2. Statck map: (mandal.lower(), gp.lower()) -> officer
    ws_statck = wb2['Statck']
    statck_map = {}
    for r in range(3, ws_statck.max_row + 1):
        mandal = clean_str(ws_statck.cell(r, 1).value)
        gp = clean_str(ws_statck.cell(r, 2).value)
        psl = clean_str(ws_statck.cell(r, 4).value)
        officer = clean_str(ws_statck.cell(r, 5).value)
        if mandal and gp and officer:
            statck_map[(mandal.lower(), gp.lower())] = officer
            if psl:
                statck_map[(mandal.lower(), psl.lower())] = officer

    print("\n=============================================================")
    print("STEP 2: Converting 1. GP Election Phase-2-2026 (437 Stations)")
    print("=============================================================")
    wb1 = openpyxl.load_workbook(wb1_path, data_only=True)
    ws1 = wb1['2nd phase']

    stations = []
    mandal_route_ps_counts = {}

    for r in range(2, ws1.max_row + 1):
        sno_val = ws1.cell(r, 1).value
        mandal = clean_str(ws1.cell(r, 2).value)
        if not mandal:
            continue
        try:
            sno = int(sno_val) if sno_val is not None else (len(stations) + 1)
        except:
            sno = len(stations) + 1

        gp_name = clean_str(ws1.cell(r, 3).value) # Name of the Gram Panchyat
        route_no = clean_str(ws1.cell(r, 4).value)
        
        # Route details - override with 2. Force if present
        route_incharge = clean_str(ws1.cell(r, 5).value)
        supporting_staff = clean_str(ws1.cell(r, 6).value)
        staying_point = clean_str(ws1.cell(r, 7).value)
        
        route_key = (mandal.lower(), route_no)
        if route_key in routes_map:
            updated_info = routes_map[route_key]
            if updated_info['incharge']:
                route_incharge = updated_info['incharge']
            if updated_info['supporting']:
                supporting_staff = updated_info['supporting']
            if updated_info['hq']:
                staying_point = updated_info['hq']

        striking_force = clean_str(ws1.cell(r, 8).value)
        special_sf = clean_str(ws1.cell(r, 9).value)
        qrt = clean_str(ws1.cell(r, 10).value)
        psname = clean_str(ws1.cell(r, 11).value) or mandal
        psl = clean_str(ws1.cell(r, 12).value)
        no_of_ps = clean_str(ws1.cell(r, 13).value)

        voters_raw = ws1.cell(r, 14).value
        try:
            no_of_voters = int(voters_raw) if voters_raw is not None else 0
        except:
            try:
                no_of_voters = int(float(str(voters_raw).strip()))
            except:
                no_of_voters = 0

        blo_contact = clean_str(ws1.cell(r, 15).value)
        dist_clean = re.sub(r'(?i)kms?|\s+', '', clean_str(ws1.cell(r, 16).value))

        cat_raw = clean_str(ws1.cell(r, 17).value).upper()
        if 'HYPER' in cat_raw or 'SENSITVIE' in cat_raw:
            cat = 'HYPER SENSITIVE'
        elif 'SENSITIVE' in cat_raw:
            cat = 'SENSITIVE'
        else:
            cat = 'NORMAL'

        asi_hc = clean_str(ws1.cell(r, 18).value) # Static Party /SI/ASI/HC
        pc = clean_str(ws1.cell(r, 19).value)     # Static Party PC
        hg = clean_str(ws1.cell(r, 20).value)     # Static Party HG
        others = clean_str(ws1.cell(r, 21).value) # Static Party Others

        # Check statck_map if static party others is empty
        if not others:
            if (mandal.lower(), gp_name.lower()) in statck_map:
                others = statck_map[(mandal.lower(), gp_name.lower())]
            elif (mandal.lower(), psl.lower()) in statck_map:
                others = statck_map[(mandal.lower(), psl.lower())]

        lat_raw = clean_str(ws1.cell(r, 22).value).rstrip(',')
        lon_raw = clean_str(ws1.cell(r, 23).value).rstrip(',')

        # Fix known coordinate typos:
        if lon_raw == '882153':
            lon_raw = '83.882153'

        route_phone = extract_phone(route_incharge)

        station_obj = {
            "id": len(stations) + 1,
            "sno": sno,
            "mandal_zptc_segment": mandal,
            "mptc_segment": gp_name, # Name of the Gram Panchyat
            "route_no": route_no,
            "route_incharge": route_incharge,
            "supporting_staff": supporting_staff,
            "staying_point": staying_point,
            "striking_force_incharge": striking_force,
            "special_striking_force_incharge": special_sf,
            "qrt": qrt,
            "psname": psname,
            "code": f"{route_no}-{sno}" if route_no else str(sno),
            "polling_station_location": psl,
            "no_of_polling_stations": no_of_ps,
            "no_of_voters": no_of_voters,
            "blo_contact_no": blo_contact,
            "distance_from_ps_kms": dist_clean,
            "categorization": cat,
            "asi_hc": asi_hc,
            "pc": pc,
            "hg": hg,
            "others": others,
            "latitude": lat_raw,
            "longitude": lon_raw,
            "route_incharge_phone": route_phone
        }
        stations.append(station_obj)

        rk = (mandal.lower(), route_no)
        mandal_route_ps_counts[rk] = mandal_route_ps_counts.get(rk, 0) + 1

    print(f"Successfully processed {len(stations)} polling stations.")

    # Write stations JSON & JS
    with open('data/stations.json', 'w', encoding='utf-8') as f:
        json.dump(stations, f, indent=4, ensure_ascii=False)
    with open('data/stations.js', 'w', encoding='utf-8') as f:
        f.write("window.INITIAL_STATIONS = " + json.dumps(stations, indent=4, ensure_ascii=False) + ";\n")

    print("\n=============================================================")
    print("STEP 3: Converting 2. Force Excel to route_mobiles datasets")
    print("=============================================================")
    all_units = []

    # 1. Route Mobiles (127 routes)
    rm_count = 0
    for r in range(2, ws_routes.max_row + 1):
        sno = ws_routes.cell(r, 1).value
        mandal = clean_str(ws_routes.cell(r, 2).value)
        route_no = clean_str(ws_routes.cell(r, 3).value)
        if not mandal or not route_no:
            continue
        incharge = clean_str(ws_routes.cell(r, 4).value)
        supp = clean_str(ws_routes.cell(r, 5).value)
        hq = clean_str(ws_routes.cell(r, 6).value)
        phone = extract_phone(incharge)
        mandal_id = mandal.replace(' ', '_').replace('.', '_')
        rm_id = f"RM_{mandal_id}_{route_no}"
        ps_cnt = mandal_route_ps_counts.get((mandal.lower(), route_no), 0)

        all_units.append({
            "id": rm_id,
            "category": "Route Mobiles",
            "categoryKey": "RM",
            "mandal": mandal,
            "route": f"RM-{route_no}",
            "unitName": f"RM-{route_no} ({hq})" if hq else f"RM-{route_no}",
            "hq": hq,
            "officer": incharge,
            "phone": phone,
            "supporting": supp,
            "pollingStations": str(ps_cnt) if ps_cnt > 0 else ""
        })
        rm_count += 1
    print(f"Processed {rm_count} Route Mobiles.")

    # 2. Striking Forces (31)
    ws_sf = wb2['Striking Forces']
    sf_count = 0
    for r in range(4, ws_sf.max_row + 1):
        sno = ws_sf.cell(r, 1).value
        gp = clean_str(ws_sf.cell(r, 2).value)
        mandal = clean_str(ws_sf.cell(r, 3).value)
        sf_no = clean_str(ws_sf.cell(r, 4).value)
        hq = clean_str(ws_sf.cell(r, 5).value)
        officer = clean_str(ws_sf.cell(r, 6).value)
        supp = clean_str(ws_sf.cell(r, 7).value)
        if not mandal or not officer:
            continue
        phone = extract_phone(officer)
        mandal_id = mandal.replace(' ', '_').replace('.', '_')
        sf_id = f"SF_{mandal_id}_{sf_no}" if sf_no else f"SF_{mandal_id}_{sf_count+1}"
        all_units.append({
            "id": sf_id,
            "category": "Striking Forces",
            "categoryKey": "SF",
            "mandal": mandal,
            "route": f"SF-{sf_no}" if sf_no else "Striking Force",
            "unitName": f"SF-{sf_no} ({hq})" if (sf_no and hq) else (f"SF ({hq})" if hq else f"SF-{sf_no}"),
            "hq": hq or gp,
            "officer": officer,
            "phone": phone,
            "supporting": supp,
            "pollingStations": ""
        })
        sf_count += 1
    print(f"Processed {sf_count} Striking Forces.")

    # 3. Special Striking Forces (26)
    ws_ssf = wb2['Special Striking Forces']
    ssf_count = 0
    for r in range(4, ws_ssf.max_row + 1):
        sno = ws_ssf.cell(r, 1).value
        gp = clean_str(ws_ssf.cell(r, 2).value)
        mandal = clean_str(ws_ssf.cell(r, 3).value)
        ssf_no = clean_str(ws_ssf.cell(r, 4).value)
        hq = clean_str(ws_ssf.cell(r, 5).value)
        officer = clean_str(ws_ssf.cell(r, 6).value)
        supp = clean_str(ws_ssf.cell(r, 7).value)
        if not mandal or not officer:
            continue
        phone = extract_phone(officer)
        mandal_id = mandal.replace(' ', '_').replace('.', '_')
        ssf_id = f"SSF_{mandal_id}_{ssf_no}" if ssf_no else f"SSF_{mandal_id}_{ssf_count+1}"
        all_units.append({
            "id": ssf_id,
            "category": "Special Striking Forces",
            "categoryKey": "SSF",
            "mandal": mandal,
            "route": f"SSF-{ssf_no}" if ssf_no else "Special Striking Force",
            "unitName": f"SSF-{ssf_no} ({hq})" if (ssf_no and hq) else (f"SSF ({hq})" if hq else f"SSF-{ssf_no}"),
            "hq": hq or gp,
            "officer": officer,
            "phone": phone,
            "supporting": supp,
            "pollingStations": ""
        })
        ssf_count += 1
    print(f"Processed {ssf_count} Special Striking Forces.")

    # 4. QRTss (5)
    ws_qrt = wb2['QRTss']
    qrt_count = 0
    for r in range(3, ws_qrt.max_row + 1):
        sno = ws_qrt.cell(r, 1).value
        panch = clean_str(ws_qrt.cell(r, 2).value)
        loc = clean_str(ws_qrt.cell(r, 3).value)
        officer = clean_str(ws_qrt.cell(r, 4).value)
        if not officer:
            continue
        phone = extract_phone(officer)
        qrt_id = f"QRT_{qrt_count+1}"
        all_units.append({
            "id": qrt_id,
            "category": "QRTs",
            "categoryKey": "QRT",
            "mandal": loc,
            "route": panch or f"QRT-{qrt_count+1}",
            "unitName": f"{panch} ({loc})" if loc else panch,
            "hq": loc,
            "officer": officer,
            "phone": phone,
            "supporting": "",
            "pollingStations": ""
        })
        qrt_count += 1
    print(f"Processed {qrt_count} QRTs.")

    # 5. Addl. SP Reserve (2)
    ws_asp = wb2['Addl. SP Reserve']
    reserve_count = 0
    for r in range(2, ws_asp.max_row + 1):
        area = clean_str(ws_asp.cell(r, 3).value)
        officer = clean_str(ws_asp.cell(r, 4).value)
        remarks = clean_str(ws_asp.cell(r, 5).value)
        if not officer:
            continue
        phone = extract_phone(officer)
        all_units.append({
            "id": f"Addl_SP_Reserve_{reserve_count+1}",
            "category": "Reserve Parties",
            "categoryKey": "RESERVE",
            "mandal": area,
            "route": f"Addl. SP Reserve - {reserve_count+1}",
            "unitName": f"Addl. SP Reserve ({area.splitlines()[0]})",
            "hq": area,
            "officer": officer,
            "phone": phone,
            "supporting": remarks,
            "pollingStations": ""
        })
        reserve_count += 1

    # 6. SP Reserve (1)
    ws_sp = wb2['SP Reserve']
    for r in range(2, ws_sp.max_row + 1):
        area = clean_str(ws_sp.cell(r, 3).value)
        officer = clean_str(ws_sp.cell(r, 4).value)
        remarks = clean_str(ws_sp.cell(r, 5).value)
        if not officer:
            continue
        phone = extract_phone(officer)
        all_units.append({
            "id": f"SP_Reserve_1",
            "category": "Reserve Parties",
            "categoryKey": "RESERVE",
            "mandal": "All Mandals",
            "route": "SP Reserve",
            "unitName": "SP Reserve (Superintendent of Police)",
            "hq": area or "Srikakulam Dist Head Quarter",
            "officer": officer,
            "phone": phone,
            "supporting": remarks,
            "pollingStations": ""
        })
        reserve_count += 1
    print(f"Processed {reserve_count} Reserve Parties (Addl. SP Reserve + SP Reserve).")

    # 7. Static Parties (from Statck sheet in 2. Force + Main)
    static_count = 0
    seen_static_officers = set()
    for r in range(3, ws_statck.max_row + 1):
        mandal = clean_str(ws_statck.cell(r, 1).value)
        gp = clean_str(ws_statck.cell(r, 2).value)
        ps_name = clean_str(ws_statck.cell(r, 3).value)
        psl = clean_str(ws_statck.cell(r, 4).value)
        officer = clean_str(ws_statck.cell(r, 5).value)
        if not mandal or not officer:
            continue
        phone = extract_phone(officer)
        unit_name = f"Static SI ({mandal} - {gp})" if gp else f"Static SI ({mandal})"
        all_units.append({
            "id": f"Static_{static_count+1}",
            "category": "Static Parties",
            "categoryKey": "STATIC",
            "mandal": mandal,
            "route": f"Static-{static_count+1}",
            "unitName": unit_name,
            "hq": psl or gp,
            "officer": officer,
            "phone": phone,
            "supporting": psl,
            "pollingStations": ""
        })
        seen_static_officers.add(phone)
        static_count += 1
    print(f"Processed {static_count} Static Parties from 2. Force.")

    # Also check if Main has additional Static SIs not yet in all_units:
    main_path = r'C:\Users\SKL-ITCORE2\Desktop\Phase-2\Main- GP Election Phase-2-2026 on 28-11-2026.xlsx'
    if os.path.exists(main_path):
        wb_main = openpyxl.load_workbook(main_path, data_only=True)
        if 'Statck' in wb_main.sheetnames:
            ws_mstatck = wb_main['Statck']
            for r in range(4, ws_mstatck.max_row + 1):
                panch = clean_str(ws_mstatck.cell(r, 3).value)
                psl = clean_str(ws_mstatck.cell(r, 4).value)
                officer = clean_str(ws_mstatck.cell(r, 5).value)
                if not officer:
                    continue
                phone = extract_phone(officer)
                if phone and phone in seen_static_officers:
                    continue
                mandal = panch
                unit_name = f"Static SI ({panch})"
                all_units.append({
                    "id": f"Static_{static_count+1}",
                    "category": "Static Parties",
                    "categoryKey": "STATIC",
                    "mandal": mandal,
                    "route": f"Static-{static_count+1}",
                    "unitName": unit_name,
                    "hq": psl or panch,
                    "officer": officer,
                    "phone": phone,
                    "supporting": psl,
                    "pollingStations": ""
                })
                seen_static_officers.add(phone)
                static_count += 1
            print(f"Total Static Parties after merging Main: {static_count}")

    # Write route_mobiles.json and route_mobiles_data.js
    with open('route_mobiles.json', 'w', encoding='utf-8') as f:
        json.dump(all_units, f, indent=4, ensure_ascii=False)
    with open('route_mobiles_data.js', 'w', encoding='utf-8') as f:
        f.write("window.ROUTE_MOBILES_DATA = " + json.dumps(all_units, indent=4, ensure_ascii=False) + ";\n")

    print(f"\nSUCCESS! Total {len(all_units)} force units written to route_mobiles.json & route_mobiles_data.js")

if __name__ == '__main__':
    run_conversion()
