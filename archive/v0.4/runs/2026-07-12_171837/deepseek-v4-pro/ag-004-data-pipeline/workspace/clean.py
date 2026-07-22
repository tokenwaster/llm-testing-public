import csv
import json
import re

rows = []
with open('data.csv', newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        email = row['email'].strip()
        score_str = row['score'].strip()
        signup = row['signup'].strip()

        # 1. Drop invalid rows
        if not email or '@' not in email:
            continue
        if not score_str:
            continue

        score = int(score_str)

        # 2. Normalize email to lowercase
        email = email.lower()

        # 3. Normalize dates
        if '/' in signup:
            # DD/MM/YYYY
            parts = signup.split('/')
            signup = f"{parts[2]}-{parts[1]}-{parts[0]}"
        # else YYYY-MM-DD, keep as is

        rows.append({'email': email, 'signup': signup, 'score': score})

# 4. Deduplicate by email: keep highest score
best = {}
for r in rows:
    e = r['email']
    if e not in best or r['score'] > best[e]['score']:
        best[e] = r

# 5. Sort by email ascending
result = sorted(best.values(), key=lambda r: r['email'])

with open('output.json', 'w') as f:
    json.dump(result, f, indent=2)

print("Done. Output:")
print(json.dumps(result, indent=2))