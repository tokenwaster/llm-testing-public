import csv
import json
from datetime import datetime

rows = []
with open('data.csv', newline='') as f:
    reader = csv.DictReader(f)
    for r in reader:
        rows.append(r)

# 1. Drop invalid rows
cleaned = []
for r in rows:
    email = (r.get('email') or '').strip()
    score_raw = (r.get('score') or '').strip()
    if '@' not in email:
        continue
    if email == '':
        continue
    if score_raw == '':
        continue
    cleaned.append({'email': email, 'signup': (r.get('signup') or '').strip(), 'score': int(score_raw)})

# 2. Normalize emails to lowercase
for r in cleaned:
    r['email'] = r['email'].lower()

# 3. Normalize dates
def normalize_date(s):
    # Try YYYY-MM-DD first
    for fmt in ('%Y-%m-%d', '%d/%m/%Y'):
        try:
            return datetime.strptime(s, fmt).strftime('%Y-%m-%d')
        except ValueError:
            continue
    raise ValueError(f'Unrecognized date format: {s!r}')

for r in cleaned:
    r['signup'] = normalize_date(r['signup'])

# 4. Deduplicate by email, keep highest score
by_email = {}
for r in cleaned:
    e = r['email']
    if e not in by_email or r['score'] > by_email[e]['score']:
        by_email[e] = r

deduped = list(by_email.values())

# 5. Sort by email ascending
deduped.sort(key=lambda r: r['email'])

# Write output.json
with open('output.json', 'w') as f:
    json.dump(deduped, f, indent=2)

# Print for verification
print(json.dumps(deduped, indent=2))
