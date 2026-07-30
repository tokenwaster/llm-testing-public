import csv
import json
import re

# Read the CSV file
with open('data.csv', 'r') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

# Step 1: Drop invalid rows (no @ in email, empty email, or empty score)
valid_rows = []
for row in rows:
    email = row.get('email', '').strip()
    signup = row.get('signup', '').strip()
    score = row.get('score', '').strip()
    
    # Skip if email is empty or contains no @
    if not email or '@' not in email:
        continue
    
    # Skip if score is empty
    if not score:
        continue
    
    valid_rows.append({
        'email': email,
        'signup': signup,
        'score': int(score)
    })

# Step 2: Normalize emails to lowercase
for row in valid_rows:
    row['email'] = row['email'].lower()

# Step 3: Normalize dates (DD/MM/YYYY -> YYYY-MM-DD)
def convert_date(date_str):
    # Check if it's already in YYYY-MM-DD format
    if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        return date_str
    # Convert DD/MM/YYYY to YYYY-MM-DD
    elif re.match(r'^\d{2}/\d{2}/\d{4}$', date_str):
        parts = date_str.split('/')
        return f"{parts[2]}-{parts[1]}-{parts[0]}"
    else:
        return date_str

for row in valid_rows:
    row['signup'] = convert_date(row['signup'])

# Step 4: Deduplicate by email - keep only the row with highest score
email_dict = {}
for row in valid_rows:
    email = row['email']
    if email not in email_dict or row['score'] > email_dict[email]['score']:
        email_dict[email] = row

unique_rows = list(email_dict.values())

# Step 5: Sort by email ascending
sorted_rows = sorted(unique_rows, key=lambda x: x['email'])

# Output as JSON array with required keys
output = []
for row in sorted_rows:
    output.append({
        'email': row['email'],
        'signup': row['signup'],
        'score': row['score']
    })

# Write to output.json
with open('output.json', 'w') as f:
    json.dump(output, f, indent=2)

print("Output written to output.json")
