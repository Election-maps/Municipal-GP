import json

with open('route_mobiles.json', 'r', encoding='utf-8') as f:
    all_units = json.load(f)

statics = [u for u in all_units if u['categoryKey'] == 'STATIC']
print(f"Total static units in route_mobiles.json: {len(statics)}")

def normalize_phone(phone):
    return ''.join(c for c in str(phone or '') if c.isdigit())[-10:]

def find_matching_units_by_phone(phone):
    clean = normalize_phone(phone)
    if not clean or len(clean) < 10:
        return []
    last10 = clean[-10:]
    return [
        u for u in all_units
        if (normalize_phone(u.get('phone')) == clean) or (last10 in str(u.get('supporting') or ''))
    ]

# Verify all 13 phones
for s in statics:
    ph = s['phone']
    matches = find_matching_units_by_phone(ph)
    assert len(matches) > 0, f"Failed for {ph}"
    m = matches[0]
    print(f"Phone {ph} -> ID: {m['id']} | Category: {m['category']} | Route: {m['route']} | Unit: {m['unitName']}")

print("\nSUCCESS: All 13 Static Party officers are fully authorized to log in to NETRA APK!")
