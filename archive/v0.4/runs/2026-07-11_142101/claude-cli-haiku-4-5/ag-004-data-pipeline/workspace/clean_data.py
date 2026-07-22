import csv
import json
from datetime import datetime

# Read the CSV file
rows = []
with open('data.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

# Step 1: Drop invalid rows
valid_rows = []
for row in rows:
    email = row.get('email', '').strip()
    score = row.get('score', '').strip()

    # Invalid if: no @, email is empty, or score is empty
    if not email or '@' not in email or not score:
        continue

    valid_rows.append({
        'email': email,
        'signup': row.get('signup', '').strip(),
        'score': score
    })

# Step 2 & 3: Normalize emails and dates
normalized_rows = []
for row in valid_rows:
    email = row['email'].lower()
    score = int(row['score'])

    # Parse and normalize date
    signup = row['signup']
    if '/' in signup:
        # DD/MM/YYYY format
        date_obj = datetime.strptime(signup, '%d/%m/%Y')
        signup = date_obj.strftime('%Y-%m-%d')
    # else it's already YYYY-MM-DD

    normalized_rows.append({
        'email': email,
        'signup': signup,
        'score': score
    })

# Step 4: Deduplicate by email, keeping highest score
email_dict = {}
for row in normalized_rows:
    email = row['email']
    if email not in email_dict or row['score'] > email_dict[email]['score']:
        email_dict[email] = row

# Convert back to list
deduplicated_rows = list(email_dict.values())

# Step 5: Sort by email ascending
deduplicated_rows.sort(key=lambda x: x['email'])

# Write to output.json
with open('output.json', 'w') as f:
    json.dump(deduplicated_rows, f, indent=2)

print("Cleaning complete. Output written to output.json")
print(f"Total records: {len(deduplicated_rows)}")
for row in deduplicated_rows:
    print(row)
