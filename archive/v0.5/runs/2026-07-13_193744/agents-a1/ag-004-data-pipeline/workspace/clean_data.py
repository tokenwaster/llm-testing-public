import csv
import json
from datetime import datetime

# Read CSV data
rows = []
with open('data.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

# Step 1: Drop invalid rows
valid_rows = []
for row in rows:
    email = row['email'].strip()
    score = row['score'].strip()
    
    # Email must not be empty and must contain @
    if not email or '@' not in email:
        continue
    
    # Score must not be empty
    if not score:
        continue
    
    valid_rows.append(row)

# Step 2: Normalize emails to lowercase
for row in valid_rows:
    row['email'] = row['email'].strip().lower()

# Step 3: Normalize dates
def normalize_date(date_str):
    date_str = date_str.strip()
    # Try YYYY-MM-DD format first
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return date_str
    except ValueError:
        pass
    
    # Try DD/MM/YYYY format
    try:
        dt = datetime.strptime(date_str, '%d/%m/%Y')
        return dt.strftime('%Y-%m-%d')
    except ValueError:
        return None

for row in valid_rows:
    normalized_date = normalize_date(row['signup'])
    if normalized_date is None:
        continue  # Skip rows with unparseable dates (though not specified, better safe)
    row['signup'] = normalized_date

# Step 4: Deduplicate by email, keep highest score per email
email_to_row = {}
for row in valid_rows:
    email = row['email']
    try:
        score = int(row['score'].strip())
    except ValueError:
        continue
    
    if email not in email_to_row:
        email_to_row[email] = (score, row)
    else:
        current_score, _ = email_to_row[email]
        if score > current_score:
            email_to_row[email] = (score, row)

# Step 5: Sort by email ascending
sorted_emails = sorted(email_to_row.keys())

# Build output JSON
output = []
for email in sorted_emails:
    _, row = email_to_row[email]
    output.append({
        'email': row['email'],
        'signup': row['signup'],
        'score': int(row['score'].strip())
    })

# Write to output.json
with open('output.json', 'w') as f:
    json.dump(output, f, indent=2)

print("Output written to output.json")
print(json.dumps(output, indent=2))
