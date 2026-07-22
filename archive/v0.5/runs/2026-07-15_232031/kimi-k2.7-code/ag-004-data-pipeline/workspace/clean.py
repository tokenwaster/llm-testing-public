import csv
import json
from collections import defaultdict
from datetime import datetime

records = []
with open('data.csv', newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        email = row.get('email', '').strip()
        signup = row.get('signup', '').strip()
        score_raw = row.get('score', '').strip()

        # Rule 1: Drop invalid rows
        if not email or '@' not in email or not score_raw:
            continue

        # Rule 2: Normalize emails to lowercase
        email = email.lower()

        # Rule 3: Normalize dates
        if '/' in signup:
            signup = datetime.strptime(signup, '%d/%m/%Y').strftime('%Y-%m-%d')

        score = int(score_raw)

        records.append({'email': email, 'signup': signup, 'score': score})

# Rule 4: Deduplicate by email, keep highest score
best = {}
for rec in records:
    email = rec['email']
    if email not in best or rec['score'] > best[email]['score']:
        best[email] = rec

# Rule 5: Sort by email ascending
result = sorted(best.values(), key=lambda r: r['email'])

with open('output.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2)

print(json.dumps(result, indent=2))
