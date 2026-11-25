import json
import re

with open('route_mobiles.json', 'r', encoding='utf-8') as f:
    all_units = json.load(f)

def normalize_phone(val):
    if not val:
        return ''
    digits = re.sub(r'\D', '', str(val)).strip()
    if len(digits) == 12 and digits.startswith('91'):
        digits = digits[2:]
    if len(digits) > 10:
        digits = digits[-10:]
    return digits

def find_matching_units_by_phone(phone):
    clean = normalize_phone(phone)
    if not clean or len(clean) < 10:
        return []
    last10 = clean[-10:]
    return [
        u for u in all_units
        if (normalize_phone(u.get('phone')) == clean or (normalize_phone(u.get('phone'))[-10:] == last10 if len(normalize_phone(u.get('phone'))) >= 10 else False))
        or (last10 in str(u.get('supporting') or ''))
        or (last10 in str(u.get('officer') or ''))
    ]

# Add1 Officers
add1_officers = [
    {"sno": 1, "area": "Sompeta", "route": "6", "name": "HC-205, BRV PS", "phone": "8639521714"},
    {"sno": 2, "area": "KAVITI", "route": "1", "name": "V.Nagaraju, CI, VR", "phone": "9948597720"},
    {"sno": 3, "area": "Srikakulam Town", "route": "QRT-2", "name": "N.V.Ramana, DSP, DAR", "phone": "6309990813"},
    {"sno": 4, "area": "Entire KSB Sub-Div.", "route": "Addl.SP Reserve", "name": "Sri P. Srinivasarao, Addl.SP, Admin", "phone": "6309990801"},
    {"sno": 5, "area": "Srikakulam & Amadalavalasa", "route": "Addl.SP Reserve", "name": "Sri Ch.Vivekananda, Addl.SP, V&E", "phone": "8008203236"},
    {"sno": 6, "area": "Amadalavalasa", "route": "Special Sticking Force", "name": "B.V Venkateswara Rao, CI, SBX", "phone": "6309990831"}
]

print("=== VERIFYING NETRA APK LOGIN FOR ALL 6 OFFICERS IN ADD1.XLSX ===")
all_passed = True
for o in add1_officers:
    ph = o["phone"]
    matched = find_matching_units_by_phone(ph)
    if matched:
        m = matched[0]
        print(f"[PASS] SNo {o['sno']} | Phone {ph} | Name: {o['name']} -> Unit ID: {m['id']} ({m['category']}: {m['unitName']})")
    else:
        print(f"[FAIL] SNo {o['sno']} | Phone {ph} | Name: {o['name']} -> NO MATCH FOUND")
        all_passed = False

assert all_passed, "Some Add1 officers failed login matching!"
print("\nALL 6 OFFICERS IN ADD1.XLSX SUCCESSFULLY VERIFIED TO LOG IN!")
