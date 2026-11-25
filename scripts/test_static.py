import openpyxl
import re

def extract_phone(val):
    if not val:
        return ''
    m = re.findall(r'\b[6-9]\d{9}\b', str(val))
    return m[0] if m else ''

wb = openpyxl.load_workbook('Routes, SF, SSF, QRTs, Reserve Parties - M &  GP 2511-14.xlsx', data_only=True)
sheet = wb['Static']
rows = list(sheet.iter_rows(min_row=2, values_only=True))

static_units = []
for idx, r in enumerate(rows, 1):
    sno = r[0]
    if sno is None or not str(sno).strip().isdigit():
        continue
    muni_type = str(r[1] or '').strip()
    force_type = str(r[2] or '').strip()
    area = str(r[3] or '').strip()
    officer = str(r[4] or '').strip()
    remarks = str(r[5] or '').strip() if len(r) > 5 and r[5] else ''
    
    phone = extract_phone(officer)
    
    mandal = area
    if 'srikakulam' in area.lower():
        mandal = 'Srikakulam'
    elif area in ['Dammalaveedhi', 'NTR M School']:
        mandal = 'Srikakulam'

    unit_name = force_type if force_type else f'Static-{idx}'
    if area:
        unit_name = f"{unit_name} ({area})"

    static_id = f"Static_{idx}"

    unit_obj = {
        'id': static_id,
        'category': 'Static Parties',
        'categoryKey': 'STATIC',
        'mandal': mandal,
        'route': force_type or f'Static-{idx}',
        'unitName': unit_name,
        'hq': area,
        'officer': officer,
        'phone': phone,
        'supporting': remarks,
        'pollingStations': ''
    }
    static_units.append(unit_obj)
    print(f"{idx}: {static_id} | {mandal} | {unit_name} | {phone} | {officer[:40]}")

print("Total parsed static units:", len(static_units))
