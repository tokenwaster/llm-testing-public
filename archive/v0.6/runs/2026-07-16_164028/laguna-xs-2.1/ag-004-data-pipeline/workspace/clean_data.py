import csv
import json
from datetime import datetime

# Read the CSV file
with open('data.csv', 'r') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

# Step 1: Drop invalid rows
valid_rows = []
for row in rows:
    email = row['email']
    score = row['score']
    
    # Check if email contains @ and is not empty
    if not email or '@' not in email:
        continue
    
    # Check if score is not empty
    if not score:
        continue
    
    valid_rows.append(row)

# Step 2: Normalize emails to lowercase
for row in valid_rows:
    row['email'] = row['email'].lower()

# Step 3: Normalize dates
for row in valid_rows:
    signup = row['signup']
    # Check if it's DD/MM/YYYY format
    if '/' in signup:
        # Parse DD/MM/YYYY and convert to YYYY-MM-DD
        dt = datetime.strptime(signup, '%d/%m/%Y')
        row['signup'] = dt.strftime('%Y-%m-%d')
    # If YYYY-MM-DD, keep as is

# Step 4: Deduplicate by email (keep highest score)
email_to_row = {}
for row in valid_rows:
    email = row['email']
    score = int(row['score'])
    
    if email not in email_to_row or score > email_to_row[email]['score_int']:
        email_to_row[email] = {
            'email': row['email'],
            'signup': row['signup'],
            'score': score,
            'score_int': score
        }

# Convert back to list with proper format
deduped_rows = []
for row in email_to_row.values():
    deduped_rows.append({
        'email': row['email'],
        'signup': row['signup'],
        'score': row['score']
    })

# Step 5: Sort by email ascending
deduped_rows.sort(key=lambda x: x['email'])

# Write to output.json
with open('output.json', 'w') as f:
    json.dump(deduped_rows, f, indent=2)

print("Done! Output written to output.json")
print(f"Total rows after cleaning: {len(deduped_rows)}")
for row in deduped_rows:
    print(row)