import csv
import json
import re

rows = []
with open('data.csv', 'r', newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        email = row['email'].strip()
        signup = row['signup'].strip()
        score_str = row['score'].strip()
        
        # Step 1: Drop invalid rows
        # - email contains no @
        # - email is empty
        # - score is empty
        if not email or '@' not in email or not score_str:
            continue
        
        # Step 2: Normalize email to lowercase
        email = email.lower()
        
        # Step 3: Normalize dates
        # Check if DD/MM/YYYY format
        if re.match(r'^\d{2}/\d{2}/\d{4}$', signup):
            dd, mm, yyyy = signup.split('/')
            signup = f"{yyyy}-{mm}-{dd}"
        # else it's already YYYY-MM-DD, keep as is
        
        # Parse score as integer
        score = int(score_str)
        
        rows.append({'email': email, 'signup': signup, 'score': score})

# Step 4: Deduplicate by email, keep highest score
best = {}
for row in rows:
    email = row['email']
    if email not in best or row['score'] > best[email]['score']:
        best[email] = row

# Step 5: Sort by email ascending
result = sorted(best.values(), key=lambda r: r['email'])

# Write output
with open('output.json', 'w') as f:
    json.dump(result, f, indent=2)

print(json.dumps(result, indent=2))
