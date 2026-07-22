import csv
import json
from datetime import datetime

with open('data.csv', 'r') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

# Step 1: Drop invalid rows
valid_rows = []
for row in rows:
    email = row.get('email', '').strip()
    score = row.get('score', '').strip()
    signup = row.get('signup', '').strip()
    
    # Invalid if email is empty, no @, or score is empty
    if not email or '@' not in email or not score:
        continue
    valid_rows.append(row)

# Step 2: Normalize emails to lowercase
for row in valid_rows:
    row['email'] = row['email'].strip().lower()

# Step 3: Normalize dates
for row in valid_rows:
    signup = row['signup'].strip()
    # Try YYYY-MM-DD first
    try:
        datetime.strptime(signup, '%Y-%m-%d')
        # Already correct format
    except ValueError:
        # Try DD/MM/YYYY
        dt = datetime.strptime(signup, '%d/%m/%Y')
        row['signup'] = dt.strftime('%Y-%m-%d')

# Step 4: Deduplicate by email, keep highest score
best = {}
for row in valid_rows:
    email = row['email']
    score = int(row['score'])
    if email not in best or score > best[email]['score']:
        best[email] = {
            'email': email,
            'signup': row['signup'],
            'score': score
        }

# Step 5: Sort by email ascending
result = sorted(best.values(), key=lambda x: x['email'])

# Write output
with open('output.json', 'w') as f:
    json.dump(result, f, indent=2)

print("Done. Output written to output.json")
print(json.dumps(result, indent=2))
