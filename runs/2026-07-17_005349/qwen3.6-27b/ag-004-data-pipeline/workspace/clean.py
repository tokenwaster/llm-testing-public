import csv
import json
import re

rows = []
with open('data.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        email = row.get('email', '').strip()
        signup = row.get('signup', '').strip()
        score = row.get('score', '').strip()

        # Rule 1: Drop invalid rows
        if not email or '@' not in email:
            continue
        if not score:
            continue

        # Rule 2: Normalize email to lowercase
        email = email.lower()

        # Rule 3: Normalize dates
        # Check if DD/MM/YYYY format
        if re.match(r'^\d{2}/\d{2}/\d{4}$', signup):
            parts = signup.split('/')
            signup = f"{parts[2]}-{parts[1]}-{parts[0]}"

        # Parse score as integer
        score = int(score)

        rows.append({
            'email': email,
            'signup': signup,
            'score': score
        })

# Rule 4: Deduplicate by email, keep highest score
best = {}
for row in rows:
    email = row['email']
    if email not in best or row['score'] > best[email]['score']:
        best[email] = row

# Rule 5: Sort by email ascending
result = sorted(best.values(), key=lambda x: x['email'])

with open('output.json', 'w') as f:
    json.dump(result, f, indent=2)

print("Done. Output written to output.json")
print(json.dumps(result, indent=2))
