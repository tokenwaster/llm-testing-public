import csv
import json
import re
from datetime import datetime

def parse_date(date_str):
    """Convert DD/MM/YYYY to YYYY-MM-DD"""
    if '/' in date_str:
        # DD/MM/YYYY format
        parts = date_str.split('/')
        day, month, year = parts[0], parts[1], parts[2]
        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
    else:
        # Already YYYY-MM-DD format
        return date_str

def is_valid_email(email):
    """Check if email contains @ and is not empty"""
    if not email or email.strip() == '':
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
    email = row.get('email', '')
    score = row.get('score', '')
    
    # Skip if email is invalid or empty
    if not is_valid_email(email):
        continue
    
    # Skip if score is empty
    if not score or score.strip() == '':
        continue
    
    valid_rows.append(row)

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
    score = int(row['score'])
    
    if email not in email_dict:
        email_dict[email] = row
    else:
        # Compare scores and keep the one with higher score
        existing_score = int(email_dict[email]['score'])
        if score > existing_score:
            email_dict[email] = row

# Step 5: Sort by email ascending
sorted_emails = sorted(email_dict.keys())

# Build final output
output = []
for email in sorted_emails:
    row = email_dict[email]
    output.append({
        "email": row['email'],
        "signup": row['signup'],
        "score": int(row['score'])
    })

# Write to JSON file
with open('output.json', 'w') as f:
    json.dump(output, f, indent=2)

print("Output written to output.json")
print(f"Total valid records: {len(output)}")
