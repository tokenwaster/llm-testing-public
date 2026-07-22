import csv
import json
import re
from datetime import datetime

def parse_date(date_str):
    """Convert DD/MM/YYYY to YYYY-MM-DD format, keep YYYY-MM-DD as is."""
    # Check if it's already in YYYY-MM-DD format
    if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        return date_str
    
    # Try DD/MM/YYYY format
    if re.match(r'^\d{2}/\d{2}/\d{4}$', date_str):
        parts = date_str.split('/')
        day, month, year = parts[0], parts[1], parts[2]
        return f"{year}-{month}-{day}"
    
    return date_str

def is_valid_email(email):
    """Check if email contains @ and is not empty."""
    if not email or email.strip() == '':
        return False
    return '@' in email

# Read the CSV file
rows = []
with open('data.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

# Step 1: Drop invalid rows (no @, empty email, or empty score)
valid_rows = []
for row in rows:
    email = row.get('email', '').strip()
    score = row.get('score', '').strip()
    
    # Skip if email is invalid or score is empty
    if not is_valid_email(email) or score == '':
        continue
    
    valid_rows.append({
        'email': email,
        'signup': row['signup'].strip(),
        'score': int(score)
    })

# Step 2: Normalize emails to lowercase
for row in valid_rows:
    row['email'] = row['email'].lower()

# Step 3: Normalize dates
for row in valid_rows:
    row['signup'] = parse_date(row['signup'])

# Step 4: Deduplicate by email, keeping highest score
email_dict = {}
for row in valid_rows:
    email = row['email']
    if email not in email_dict or row['score'] > email_dict[email]['score']:
        email_dict[email] = row

# Get deduplicated rows
deduped_rows = list(email_dict.values())

# Step 5: Sort by email ascending
sorted_rows = sorted(deduped_rows, key=lambda x: x['email'])

# Format output with only required keys
output = []
for row in sorted_rows:
    output.append({
        'email': row['email'],
        'signup': row['signup'],
        'score': row['score']
    })

# Write to JSON file
with open('output.json', 'w') as f:
    json.dump(output, f, indent=2)

print("Output written to output.json")
print(f"Total valid records: {len(output)}")
