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
    print("=============================================================")
    print("STEP 1: Converting Municipality & GP Data for Google Map on 2511-14.xlsx")
    print("=============================================================")
    wb_st = openpyxl.load_workbook("Municipality & GP Data for Google Map on 2511-14.xlsx", data_only=True)
    ws_st = wb_st['Muncipal']

    stations = []
    mandal_route_ps_counts = {}

    current_route_no = ""
    current_mandal = ""
    current_incharge = ""
    current_supporting = ""
    current_staying = ""

    rows = list(ws_st.iter_rows(min_row=2, values_only=True))
    for idx, r in enumerate(rows, 1):
        sno_raw = r[0]
        if sno_raw is None and r[2] is None:
            continue
        try:
            sno = int(sno_raw) if sno_raw is not None else idx
        except:
            sno = idx

        mandal_muni = clean_str(r[2])
        ward_segment = clean_str(r[3])
        route_no_raw = clean_str(r[4])
        route_incharge_raw = clean_str(r[5])
        supporting_staff_raw = clean_str(r[6])
        staying_point_raw = clean_str(r[7])

        if route_no_raw != "":
            current_route_no = route_no_raw
            current_mandal = mandal_muni
            current_incharge = route_incharge_raw
            current_supporting = supporting_staff_raw
            current_staying = staying_point_raw
            route_no = route_no_raw
            route_incharge = route_incharge_raw
            supporting_staff = supporting_staff_raw
            staying_point = staying_point_raw
        else:
            if mandal_muni == current_mandal or not mandal_muni:
                route_no = current_route_no
                route_incharge = route_incharge_raw or current_incharge
                supporting_staff = supporting_staff_raw or current_supporting
                staying_point = staying_point_raw or current_staying
            else:
                route_no = ""
                route_incharge = route_incharge_raw
                supporting_staff = supporting_staff_raw
                staying_point = staying_point_raw

        striking_force = clean_str(r[8])
        special_sf = clean_str(r[9])
        qrt = clean_str(r[10])
        psname = clean_str(r[11]) or mandal_muni

        code_raw = r[12]
        if isinstance(code_raw, (datetime.datetime, datetime.date)):
            code = f"{code_raw.month}-{code_raw.day}"
        else:
            code = clean_str(code_raw)

        psl = clean_str(r[13])
        no_of_ps = clean_str(r[14])
        
        voters_raw = r[15]
        try:
            no_of_voters = int(voters_raw) if voters_raw is not None else 0
        except:
            try:
                no_of_voters = int(float(str(voters_raw).strip()))
            except:
                no_of_voters = 0

        blo_contact = clean_str(r[16])
        dist_clean = re.sub(r'(?i)kms?|\s+', '', clean_str(r[17]))

        cat_raw = clean_str(r[18]).upper()
        if 'HYPER' in cat_raw or 'SENSITVIE' in cat_raw:
            cat = 'HYPER SENSITIVE'
        elif 'SENSITIVE' in cat_raw:
            cat = 'SENSITIVE'
        else:
            cat = 'NORMAL'

        asi_hc = clean_str(r[19])
        pc = clean_str(r[20])
        hg = clean_str(r[21])
        others = clean_str(r[22])

        lat_raw = clean_str(r[23]).rstrip(',')
        lon_raw = clean_str(r[24]).rstrip(',')

        if sno == 70:
            lon_raw = '83.8684'
        elif sno == 85:
            lon_raw = '83.895117'
        elif sno in (205, 206):
            lat_raw = '18.862093'
            lon_raw = '84.509315'
        elif sno == 243:
            lon_raw = '84.45476'
        elif sno == 90:
            lat_raw = '18.31313'
            lon_raw = '83.876209'
        elif sno == 355 or '18.7239942' in lat_raw:
            lat_raw = '18.723945'
            lon_raw = '84.461552'
        elif sno == 377 or '80.404696' in lon_raw or '18.711484' in lat_raw or '8.711484' in lat_raw:
            lat_raw = '18.313155306466673'
            lon_raw = '83.89630250580744'
        
        route_phone = extract_phone(route_incharge)

        station_obj = {
            "id": idx,
            "sno": sno,
            "mandal_zptc_segment": mandal_muni,
            "mptc_segment": ward_segment,
            "route_no": route_no,
            "route_incharge": route_incharge,
            "supporting_staff": supporting_staff,
            "staying_point": staying_point,
            "striking_force_incharge": striking_force,
            "special_striking_force_incharge": special_sf,
            "qrt": qrt,
            "psname": psname,
            "code": code,
            "polling_station_location": psl,
            "no_of_polling_stations": no_of_ps,
            "no_of_voters": no_of_voters,
            "blo_contact_no": blo_contact,
            "distance_from_ps_kms": dist_clean,
            "categorization": cat,
            "si": "",
            "asi_hc": asi_hc,
            "pc": pc,
            "hg": hg,
            "others": others,
            "latitude": lat_raw,
            "longitude": lon_raw,
            "route_staff": route_incharge,
            "route_staff_ph_no": route_phone
        }
        stations.append(station_obj)

        key = (mandal_muni.lower(), route_no)
        mandal_route_ps_counts[key] = mandal_route_ps_counts.get(key, 0) + 1

    # Apply Add1 updates directly to stations
    for s in stations:
        mandal_lower = str(s.get('mandal_zptc_segment', '')).lower()
        r_no = str(s.get('route_no', '')).strip()

        # 1. Sompeta Route 6 (HC-205, BRV PS, 8639521714)
        if 'sompeta' in mandal_lower and r_no == '6':
            s['route_incharge'] = "HC-205, BRV PS,\n8639521714"
            s['route_staff'] = "HC-205, BRV PS,\n8639521714"
            s['route_staff_ph_no'] = "8639521714"

        # 2. Kaviti Special Striking Force (V.Nagaraju, CI, VR, Srikakulam, 9948597720)
        elif 'kaviti' in mandal_lower:
            s['special_striking_force_incharge'] = "V.Nagaraju, CI, VR, Srikakulam\n 9948597720"

        # 3. Amadalavalasa Special Striking Force (M.Nageswara Rao and B.V Venkateswara Rao)
        elif 'amadalavalasa' in mandal_lower and ('7013269612' in str(s.get('special_striking_force_incharge', '')) or s.get('sno') in (1, 5, 8, 9, 10, 27, 28, 29)):
            s['special_striking_force_incharge'] = "CI/VR M.Nageswararao 7013269612 / B.V Venkateswara Rao, CI, SBX 6309990831"

        # 4. Srikakulam Town QRT (N.V.Ramana, DSP, DAR, Srikakulam, 6309990813)
        elif 'srikakulam' in mandal_lower:
            s['qrt'] = "Ch. Dhanunjaya Naidu, SDPO, 6309990804 / N.V.Ramana, DSP, DAR, Srikakulam, 6309990813"

    print(f"Generated {len(stations)} station records.")
    with open('data/stations.json', 'w', encoding='utf-8') as f:
        json.dump(stations, f, indent=4, ensure_ascii=False)
    with open('data/stations.js', 'w', encoding='utf-8') as f:
        f.write("window.INITIAL_STATIONS = " + json.dumps(stations, indent=4, ensure_ascii=False) + ";\n")

    print("\n=============================================================")
    print("STEP 2: Converting Routes, SF, SSF, QRTs, Reserve Parties - M &  GP 2511-14.xlsx")
    print("=============================================================")
    wb_rt = openpyxl.load_workbook("Routes, SF, SSF, QRTs, Reserve Parties - M &  GP 2511-14.xlsx", data_only=True)
    all_units = []

    # 1. Route Mobiles (Strictly SNo 1 to 98)
    ws_rm = wb_rt['Route Mobiles']
    rm_rows = list(ws_rm.iter_rows(min_row=3, values_only=True))
    rm_count = 0
    for idx, r in enumerate(rm_rows, 1):
        sno = r[0]
        mandal = clean_str(r[2])
        if sno is None or not str(sno).strip().isdigit() or not mandal:
            continue
        
        route_no = clean_str(r[3])
        officer = clean_str(r[4])
        supporting = clean_str(r[5])
        hq = clean_str(r[6])
        phone = extract_phone(officer)
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
            "officer": officer,
            "phone": phone,
            "supporting": supporting,
            "pollingStations": str(ps_cnt) if ps_cnt > 0 else ""
        })
        rm_count += 1
    print(f"Processed {rm_count} Route Mobiles.")

    # 2. Striking Forces (26)
    ws_sf = wb_rt['Striking Forces']
    sf_rows = list(ws_sf.iter_rows(min_row=4, values_only=True))
    sf_count = 0
    for idx, r in enumerate(sf_rows, 1):
        sno = r[0]
        mandal = clean_str(r[2])
        if sno is None or not str(sno).strip().isdigit() or not mandal:
            continue
        sf_no = clean_str(r[3])
        hq = clean_str(r[4])
        officer = clean_str(r[5])
        supporting = clean_str(r[6]) if len(r) > 6 else ""
        phone = extract_phone(officer)
        mandal_id = mandal.replace(' ', '_').replace('.', '_')
        sf_id = f"SF_{mandal_id}_{sf_no}"
        all_units.append({
            "id": sf_id,
            "category": "Striking Forces",
            "categoryKey": "SF",
            "mandal": mandal,
            "route": f"SF-{sf_no}",
            "unitName": f"SF-{sf_no} ({hq})" if hq else f"SF-{sf_no}",
            "hq": hq,
            "officer": officer,
            "phone": phone,
            "supporting": supporting,
            "pollingStations": ""
        })
        sf_count += 1
    print(f"Processed {sf_count} Striking Forces.")

    # 3. Special Striking Forces (23)
    ws_ssf = wb_rt['Special Striking Forces']
    ssf_rows = list(ws_ssf.iter_rows(min_row=4, values_only=True))
    ssf_count = 0
    for idx, r in enumerate(ssf_rows, 1):
        sno = r[0]
        mandal = clean_str(r[2])
        if sno is None or not str(sno).strip().isdigit() or not mandal:
            continue
        ssf_no = clean_str(r[3])
        hq = clean_str(r[4])
        officer = clean_str(r[5])
        supporting = clean_str(r[6]) if len(r) > 6 else ""
        phone = extract_phone(officer)
        mandal_id = mandal.replace(' ', '_').replace('.', '_')
        ssf_id = f"SSF_{mandal_id}_{ssf_no}"
        all_units.append({
            "id": ssf_id,
            "category": "Special Striking Forces",
            "categoryKey": "SSF",
            "mandal": mandal,
            "route": f"SSF-{ssf_no}",
            "unitName": f"SSF ({hq})" if hq else f"SSF-{ssf_no}",
            "hq": hq,
            "officer": officer,
            "phone": phone,
            "supporting": supporting,
            "pollingStations": ""
        })
        ssf_count += 1
    print(f"Processed {ssf_count} Special Striking Forces.")

    # 4. QRTss (5)
    ws_qrt = wb_rt['QRTss']
    qrt_rows = list(ws_qrt.iter_rows(min_row=3, values_only=True))
    qrt_count = 0
    for idx, r in enumerate(qrt_rows, 1):
        sno = r[0]
        if sno is None or not str(sno).strip().isdigit():
            continue
        force_type = clean_str(r[2])
        hq = clean_str(r[3])
        officer = clean_str(r[4])
        if not officer:
            continue
        phone = extract_phone(officer)
        qrt_id = f"QRT_{idx}"
        all_units.append({
            "id": qrt_id,
            "category": "QRTs",
            "categoryKey": "QRT",
            "mandal": hq,
            "route": force_type or f"QRT-{idx}",
            "unitName": f"{force_type} ({hq})" if hq else force_type,
            "hq": hq,
            "officer": officer,
            "phone": phone,
            "supporting": "",
            "pollingStations": ""
        })
        qrt_count += 1
    print(f"Processed {qrt_count} QRTs.")

    # 5. Reserve Parties - ONLY Addl. SP Reserve and HQ-Resereve Parties (Total 5)
    reserve_count = 0
    # Addl. SP Reserve (2)
    ws_asp = wb_rt['Addl. SP Reserve']
    asp_rows = list(ws_asp.iter_rows(min_row=3, values_only=True))
    for idx, r in enumerate(asp_rows, 1):
        sno = r[0]
        if sno is None or not str(sno).strip().isdigit():
            continue
        force_type = clean_str(r[2])
        area = clean_str(r[3])
        officer = clean_str(r[4])
        remarks = clean_str(r[5]) if len(r) > 5 else ""
        if not officer:
            continue
        phone = extract_phone(officer)
        all_units.append({
            "id": f"Addl_SP_Reserve_{idx}",
            "category": "Reserve Parties",
            "categoryKey": "RESERVE",
            "mandal": area,
            "route": f"Addl. SP Reserve - {idx}",
            "unitName": f"Addl. SP Reserve ({area})",
            "hq": area,
            "officer": officer,
            "phone": phone,
            "supporting": remarks,
            "pollingStations": ""
        })
        reserve_count += 1

    # HQ-Resereve Parties (3)
    ws_hqr = wb_rt['HQ-Resereve Parties']
    hqr_rows = list(ws_hqr.iter_rows(min_row=3, values_only=True))
    for idx, r in enumerate(hqr_rows, 1):
        sno = r[0]
        if sno is None or not str(sno).strip().isdigit():
            continue
        force_type = clean_str(r[2])
        area = clean_str(r[3])
        officer = clean_str(r[4])
        remarks = clean_str(r[5]) if len(r) > 5 else ""
        if not officer:
            continue
        phone = extract_phone(officer)
        all_units.append({
            "id": f"HQ_Reserve_{idx}",
            "category": "Reserve Parties",
            "categoryKey": "RESERVE",
            "mandal": area,
            "route": f"HQ Reserve - {idx}",
            "unitName": f"HQ Reserve ({area})",
            "hq": area,
            "officer": officer,
            "phone": phone,
            "supporting": remarks,
            "pollingStations": ""
        })
        reserve_count += 1

    print(f"Processed {reserve_count} Reserve Parties (Addl. SP Reserve + HQ-Reserve Parties).")

    # 6. Static Parties (13)
    static_count = 0
    if 'Static' in wb_rt.sheetnames:
        ws_static = wb_rt['Static']
        static_rows = list(ws_static.iter_rows(min_row=2, values_only=True))
        for idx, r in enumerate(static_rows, 1):
            sno = r[0]
            if sno is None or not str(sno).strip().isdigit():
                continue
            muni_type = clean_str(r[1])
            force_type = clean_str(r[2])
            area = clean_str(r[3])
            officer = clean_str(r[4])
            remarks = clean_str(r[5]) if len(r) > 5 else ""
            if not officer:
                continue
            phone = extract_phone(officer)
            mandal = area
            if 'srikakulam' in area.lower():
                mandal = 'Srikakulam'
            elif area in ['Dammalaveedhi', 'NTR M School']:
                mandal = 'Srikakulam'

            unit_name = force_type if force_type else f"Static-{idx}"
            if area:
                unit_name = f"{unit_name} ({area})"

            static_id = f"Static_{idx}"
            all_units.append({
                "id": static_id,
                "category": "Static Parties",
                "categoryKey": "STATIC",
                "mandal": mandal,
                "route": force_type or f"Static-{idx}",
                "unitName": unit_name,
                "hq": area,
                "officer": officer,
                "phone": phone,
                "supporting": remarks,
                "pollingStations": ""
            })
            static_count += 1
    print(f"Processed {static_count} Static Parties.")

    # 7. Apply Add1.xlsx Updates (6 Officers)
    add1_path = "Add1.xlsx"
    if os.path.exists(add1_path):
        wb_add1 = openpyxl.load_workbook(add1_path, data_only=True)
        ws_add1 = wb_add1.active
        add1_count = 0
        for r in list(ws_add1.iter_rows(min_row=2, values_only=True)):
            if not r or not any(r):
                continue
            sno, area_type, mandal_raw, route_raw, officer_raw, phone_raw = r[:6]
            if not phone_raw:
                continue
            clean_phone_val = extract_phone(str(phone_raw))
            officer_str = clean_str(officer_raw)
            mandal_str = clean_str(mandal_raw)
            route_str = clean_str(route_raw)

            # 1. Sompeta Route 6 (RM_Sompeta_6)
            if 'sompeta' in mandal_str.lower() and ('6' in route_str or 'rm-6' in route_str.lower()):
                for u in all_units:
                    if u['id'] == 'RM_Sompeta_6':
                        old_off = u.get('officer', '')
                        u['officer'] = officer_str
                        u['phone'] = clean_phone_val
                        if old_off and clean_phone_val not in old_off:
                            u['supporting'] = old_off + ';\n' + u.get('supporting', '')
                        add1_count += 1

            # 2. Kaviti Route 1 (SSF_KAVITI_1)
            elif 'kaviti' in mandal_str.lower() and ('1' in route_str):
                for u in all_units:
                    if u['id'] == 'SSF_KAVITI_1':
                        u['officer'] = officer_str
                        u['phone'] = clean_phone_val
                        add1_count += 1

            # 3. Srikakulam Town QRT-2 (QRT_4)
            elif 'srikakulam' in mandal_str.lower() and 'qrt-2' in route_str.lower():
                for u in all_units:
                    if u['id'] == 'QRT_4' or (u['categoryKey'] == 'QRT' and 'srikakulam' in u['mandal'].lower() and '2' in u['route'].lower()):
                        u['officer'] = officer_str
                        u['phone'] = clean_phone_val
                        add1_count += 1

            # 4. Entire KSB Sub-Div. Addl.SP Reserve (Addl_SP_Reserve_1)
            elif 'ksb' in mandal_str.lower() or 'kasibugga' in mandal_str.lower() or ('addl' in route_str.lower() and str(sno) == '4'):
                for u in all_units:
                    if u['id'] == 'Addl_SP_Reserve_1':
                        u['officer'] = officer_str
                        u['phone'] = clean_phone_val
                        add1_count += 1

            # 5. Srikakulam & Amadalavalasa Addl.SP Reserve (Addl_SP_Reserve_2)
            elif ('srikakulam' in mandal_str.lower() and 'amadalavalasa' in mandal_str.lower()) or ('addl' in route_str.lower() and str(sno) == '5'):
                for u in all_units:
                    if u['id'] == 'Addl_SP_Reserve_2':
                        u['officer'] = officer_str
                        u['phone'] = clean_phone_val
                        add1_count += 1

            # 6. Amadalavalasa Special Striking Force (B.V Venkateswara Rao, CI, SBX, 6309990831 from Add1)
            elif 'amadalavalasa' in mandal_str.lower() and ('sticking' in route_str.lower() or 'striking' in route_str.lower() or 'ssf' in route_str.lower()):
                all_units.append({
                    "id": "SSF_Amadalavalasa_SBX",
                    "category": "Special Striking Forces",
                    "categoryKey": "SSF",
                    "mandal": mandal_str or "Amadalavalasa",
                    "route": "Special Striking Force",
                    "unitName": "SSF (Amadalavalasa - CI SBX)",
                    "hq": "Amadalavalasa",
                    "officer": officer_str,
                    "phone": clean_phone_val,
                    "supporting": "",
                    "pollingStations": ""
                })
                add1_count += 1

        print(f"Applied updates for {add1_count} officers from Add1.xlsx.")

    print(f"\nTOTAL ALL UNITS: {len(all_units)}")
    from collections import Counter
    print("Breakdown:", Counter(u['category'] for u in all_units))

    with open('route_mobiles.json', 'w', encoding='utf-8') as f:
        json.dump(all_units, f, indent=4, ensure_ascii=False)
    with open('route_mobiles_data.js', 'w', encoding='utf-8') as f:
        f.write("window.ROUTE_MOBILES_DATA = " + json.dumps(all_units, indent=4, ensure_ascii=False) + ";\n")
    print("Saved route_mobiles.json and route_mobiles_data.js successfully.")

if __name__ == '__main__':
    run_conversion()
