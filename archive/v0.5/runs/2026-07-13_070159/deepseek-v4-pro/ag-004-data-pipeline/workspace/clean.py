import csv
import json
import re
from datetime import datetime

def parse_date(s):
    """Parse a date string, returning YYYY-MM-DD format."""
    s = s.strip()
    # Try YYYY-MM-DD first
    if re.match(r'^\d{4}-\d{2}-\d{2}$', s):
        return s
    # Try DD/MM/YYYY
    if re.match(r'^\d{2}/\d{2}/\d{4}$', s):
        dt = datetime.strptime(s, '%d/%m/%Y')
        return dt.strftime('%Y-%m-%d')
    raise ValueError(f"Unknown date format: {s}")

# Read CSV
rows = []
with open('data.csv', newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        email = row.get('email', '').strip()
        signup = row.get('signup', '').strip()
        score = row.get('score', '').strip()
        rows.append({'email': email, 'signup': signup, 'score': score})

# Step 1: Drop invalid rows
valid = []
for r in rows:
    email = r['email']
    score = r['score']
    if not email or '@' not in email:
        continue
    if not score:
        continue
    valid.append(r)

# Step 2: Normalize emails to lowercase
for r in valid:
    r['email'] = r['email'].lower()

# Step 3: Normalize dates
for r in valid:
    r['signup'] = parse_date(r['signup'])

# Step 4: Deduplicate by email, keep highest score
best = {}
for r in valid:
    email = r['email']
    score = int(r['score'])
    if email not in best or score > int(best[email]['score']):
        best[email] = r

# Step 5: Sort by email ascending
result = sorted(best.values(), key=lambda r: r['email'])

# Ensure score is integer
for r in result:
    r['score'] = int(r['score'])

# Write output
with open('output.json', 'w') as f:
    json.dump(result, f, indent=2)

print("Done. Output records:")
for r in result:
    print(r)