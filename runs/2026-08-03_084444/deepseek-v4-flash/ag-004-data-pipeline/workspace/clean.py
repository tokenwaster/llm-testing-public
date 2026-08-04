import csv
import json
from collections import OrderedDict

# Read data
with open('data.csv', newline='') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

# Step 1: Drop invalid rows
valid_rows = []
for r in rows:
    email = (r.get('email') or '').strip()
    score = (r.get('score') or '').strip()
    if not email or '@' not in email:
        continue
    if not score:
        continue
    valid_rows.append(r)

# Step 2: Normalize emails to lowercase
for r in valid_rows:
    r['email'] = r['email'].strip().lower()

# Step 3: Normalize dates
def normalize_date(d):
    d = d.strip()
    if d.count('-') == 2:  # YYYY-MM-DD
        parts = d.split('-')
        if len(parts[0]) == 4:  # already YYYY-MM-DD
            return d
    if d.count('/') == 2:  # DD/MM/YYYY
        parts = d.split('/')
        return f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
    return d  # fallback

for r in valid_rows:
    r['signup'] = normalize_date(r.get('signup', ''))

# Step 4: Deduplicate by email, keep highest score
best = {}
for r in valid_rows:
    email = r['email']
    score = int(r['score'])
    if email not in best or score > best[email]['score']:
        best[email] = {'email': email, 'signup': r['signup'], 'score': score}

# Step 5: Sort by email ascending
result = sorted(best.values(), key=lambda x: x['email'])

# Write output
with open('output.json', 'w') as f:
    json.dump(result, f, indent=2)

print("Output written to output.json")
print(json.dumps(result, indent=2))