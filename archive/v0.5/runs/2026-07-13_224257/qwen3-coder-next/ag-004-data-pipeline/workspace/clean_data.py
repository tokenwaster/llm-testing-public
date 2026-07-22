import csv
import json
import re
from datetime import datetime

def parse_date(date_str):
    """Convert DD/MM/YYYY to YYYY-MM-DD format."""
    if '/' in date_str:
        # DD/MM/YYYY format
        dt = datetime.strptime(date_str, "%d/%m/%Y")
        return dt.strftime("%Y-%m-%d")
    else:
        # Already YYYY-MM-DD format
        return date_str

def is_valid_email(email):
    """Check if email contains @ and is not empty."""
    if not email or email.strip() == "":
        return False
    return '@' in email

# Read the CSV file
rows = []
with open('data.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

# Step 1: Drop invalid rows (email contains no @, email is empty, or score is empty)
valid_rows = []
for row in rows:
    email = row.get('email', '').strip()
    score = row.get('score', '').strip()
    
    # Skip if email is invalid or empty
    if not is_valid_email(email):
        continue
    
    # Skip if score is empty
    if score == "":
        continue
    
    valid_rows.append({
        'email': email,
        'signup': row.get('signup', '').strip(),
        'score': score
    })

# Step 2: Normalize emails to lowercase
for row in valid_rows:
    row['email'] = row['email'].lower()

# Step 3: Normalize dates
for row in valid_rows:
    row['signup'] = parse_date(row['signup'])

# Step 4: Deduplicate by email - keep only the row with highest score
email_dict = {}
for row in valid_rows:
    email = row['email']
    if email not in email_dict or int(row['score']) > int(email_dict[email]['score']):
        email_dict[email] = row

# Get deduplicated rows
deduped_rows = list(email_dict.values())

# Step 5: Sort by email ascending
sorted_rows = sorted(deduped_rows, key=lambda x: x['email'])

# Format output with correct types
output = []
for row in sorted_rows:
    output.append({
        'email': row['email'],
        'signup': row['signup'],
        'score': int(row['score'])
    })

# Write to JSON file
with open('output.json', 'w') as f:
    json.dump(output, f, indent=2)

print("Cleaned data written to output.json")
print(f"Total valid records: {len(output)}")
