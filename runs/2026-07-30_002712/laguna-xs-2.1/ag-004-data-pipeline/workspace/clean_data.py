import csv
import json
from datetime import datetime

# Read CSV
with open('data.csv', 'r') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

# Step 1: Drop invalid rows
valid_rows = []
for row in rows:
    email = row['email']
    score = row['score']
    # Check if email is empty or has no @, or score is empty
    if not email or '@' not in email:
        continue
    if not score:
        continue
    valid_rows.append(row)

# Step 2: Normalize emails to lowercase
for row in valid_rows:
    row['email'] = row['email'].lower()

# Step 3: Normalize dates
def normalize_date(date_str):
    # Try YYYY-MM-DD format first
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        return date_str  # Already in correct format
    except ValueError:
        pass
    
    # Try DD/MM/YYYY format
    try:
        dt = datetime.strptime(date_str, '%d/%m/%Y')
        return dt.strftime('%Y-%m-%d')
    except ValueError:
        pass
    
    return date_str  # Return as is if no match

for row in valid_rows:
    row['signup'] = normalize_date(row['signup'])

# Step 4: Deduplicate by email - keep highest score per email
email_to_row = {}
for row in valid_rows:
    email = row['email']
    score = int(row['score'])
    if email not in email_to_row or score > int(email_to_row[email]['score']):
        email_to_row[email] = row

deduped_rows = list(email_to_row.values())

# Step 5: Sort by email ascending
sorted_rows = sorted(deduped_rows, key=lambda x: x['email'])

# Create output with required format
output = []
for row in sorted_rows:
    output.append({
        'email': row['email'],
        'signup': row['signup'],
        'score': int(row['score'])
    })

# Write to JSON
with open('output.json', 'w') as f:
    json.dump(output, f, indent=2)

print("Cleaned data written to output.json")
print(f"Total records: {len(output)}")
for record in output:
    print(record)