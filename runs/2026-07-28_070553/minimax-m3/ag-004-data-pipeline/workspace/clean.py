import csv
import json
from datetime import datetime

rows = []
with open('data.csv', newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        email = (row.get('email') or '').strip()
        signup = (row.get('signup') or '').strip()
        score_raw = (row.get('score') or '').strip()

        # Rule 1: drop invalid rows
        if '@' not in email or not email or not score_raw:
            continue

        # Rule 2: normalize email
        email = email.lower()

        # Rule 3: normalize date
        if signup:
            for fmt in ('%Y-%m-%d', '%d/%m/%Y'):
                try:
                    signup = datetime.strptime(signup, fmt).strftime('%Y-%m-%d')
                    break
                except ValueError:
                    continue

        score = int(score_raw)
        rows.append({'email': email, 'signup': signup, 'score': score})

# Rule 4: dedupe by email, keep highest score
best = {}
for r in rows:
    if r['email'] not in best or r['score'] > best[r['email']]['score']:
        best[r['email']] = r

# Rule 5: sort by email ascending
result = sorted(best.values(), key=lambda r: r['email'])

with open('output.json', 'w') as f:
    json.dump(result, f, indent=2)

print(json.dumps(result, indent=2))
