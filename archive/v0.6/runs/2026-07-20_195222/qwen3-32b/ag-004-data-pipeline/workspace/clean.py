import csv
from datetime import datetime
import json

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        try:
            return datetime.strptime(date_str, "%d/%m/%Y")
        except ValueError as e:
            raise ValueError(f"Date {date_str} is invalid") from e

valid_rows = []
with open('data.csv', 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        email = row['email'].strip()
        score_str = row['score'].strip()
        date_str = row['signup'].strip()

        # Rule 1: Drop invalid rows
        if '@' not in email or len(email) == 0:
            continue
        if len(score_str) == 0:
            continue

        normalized_email = email.lower()

        try:
            parsed_date = parse_date(date_str)
            signup_normalized = parsed_date.strftime("%Y-%m-%d")
        except ValueError:
            # Skip rows with invalid date format
            continue

        try:
            score = int(score_str)
        except ValueError:
            # Invalid score, skip row
            continue

        valid_rows.append({
            'email': normalized_email,
            'signup': signup_normalized,
            'score': score
        })

# Deduplicate by email, keeping highest score
dedup_dict = {}
for row in valid_rows:
    email = row['email']
    current_score = row['score']
    if email not in dedup_dict or current_score > dedup_dict[email]['score']:
        dedup_dict[email] = row

sorted_list = sorted(dedup_dict.values(), key=lambda x: x['email'])

# Write to output.json
with open('output.json', 'w') as f:
    json.dump(sorted_list, f)