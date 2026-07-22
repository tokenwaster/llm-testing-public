#!/usr/bin/env python3
import csv
import json
from datetime import datetime

def parse_date(date_str):
    """Convert date to YYYY-MM-DD format."""
    if not date_str:
        return None

    # Try YYYY-MM-DD first
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').strftime('%Y-%m-%d')
    except ValueError:
        pass

    # Try DD/MM/YYYY
    try:
        return datetime.strptime(date_str, '%d/%m/%Y').strftime('%Y-%m-%d')
    except ValueError:
        pass

    return None

def is_valid_row(email, signup, score):
    """Check if a row is valid."""
    # Must have @ in email
    if '@' not in email:
        return False
    # Email must not be empty (already checked by @, but explicit)
    if not email:
        return False
    # Score must not be empty
    if not score:
        return False
    return True

# Read CSV
rows = []
with open('data.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        email = row['email'].strip()
        signup = row['signup'].strip()
        score = row['score'].strip()

        # Skip invalid rows
        if not is_valid_row(email, signup, score):
            continue

        # Normalize email to lowercase
        email = email.lower()

        # Parse and normalize date
        parsed_date = parse_date(signup)
        if not parsed_date:
            continue

        # Convert score to int
        try:
            score_int = int(score)
        except ValueError:
            continue

        rows.append({
            'email': email,
            'signup': parsed_date,
            'score': score_int
        })

# Deduplicate by email, keeping highest score
email_map = {}
for row in rows:
    email = row['email']
    if email not in email_map or row['score'] > email_map[email]['score']:
        email_map[email] = row

# Convert back to list and sort by email
result = sorted(email_map.values(), key=lambda x: x['email'])

# Write JSON
with open('output.json', 'w') as f:
    json.dump(result, f, indent=2)

print(f"Cleaned {len(result)} records")
for record in result:
    print(record)
