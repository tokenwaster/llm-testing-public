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
    # Check if email contains @ and is not empty, and score is not empty
    if email and '@' in email and score:
        valid_rows.append(row)

# Step 2: Normalize emails to lowercase
for row in valid_rows:
    row['email'] = row['email'].lower()

# Step 3: Normalize dates
for row in valid_rows:
    signup = row['signup']
    if '/' in signup:
        # DD/MM/YYYY format
        day, month, year = signup.split('/')
        row['signup'] = f"{year}-{month}-{day}"
    # else YYYY-MM-DD format, keep as is

# Step 4: Deduplicate by email (keep highest score)
email_to_row = {}
for row in valid_rows:
    email = row['email']
    score = int(row['score'])
    if email not in email_to_row or score > email_to_row[email]['score_int']:
        email_to_row[email] = {'row': row, 'score_int': score}

# Convert to list and convert score to int
result = []
for entry in email_to_row.values():
    row = entry['row']
    result.append({
        'email': row['email'],
        'signup': row['signup'],
        'score': entry['score_int']
    })

# Step 5: Sort by email ascending
result.sort(key=lambda x: x['email'])

# Write to output.json
with open('output.json', 'w') as f:
    json.dump(result, f, indent=2)

print("Done! Output written to output.json")
print(f"Total records: {len(result)}")
for r in result:
    print(r)