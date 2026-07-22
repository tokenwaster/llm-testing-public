import csv
import json
from datetime import datetime

def normalize_date(date_str):
    try:
        # Check for YYYY-MM-DD format
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except ValueError:
        pass

    # Process DD/MM/YYYY format
    try:
        day, month, year = map(int, date_str.split('/'))
        return f"{year:04d}-{month:02d}-{day:02d}"
    except (ValueError, TypeError):
        raise ValueError(f"Invalid date format: {date_str}")

def main():
    rows = []
    with open('data.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row['email'].strip()
            signup_date = row['signup'].strip()
            score_str = row.get('score', '').strip()

            # Rule 1: Drop invalid rows
            if '@' not in email or len(email) == 0 or len(score_str) == 0:
                continue

            try:
                score = int(score_str)
            except ValueError:
                continue

            # Rule 2: Normalize email to lowercase
            normalized_email = email.lower()

            # Rule 3: Normalize date
            try:
                normalized_signup_date = normalize_date(signup_date)
            except ValueError:
                continue

            rows.append({
                'email': normalized_email,
                'signup': normalized_signup_date,
                'score': score
            })

    # Rule 4: Deduplicate by email (keep highest score)
    email_dict = {}
    for row in rows:
        if (row['email'] not in email_dict or 
            row['score'] > email_dict[row['email']]['score']):
            email_dict[row['email']] = row

    # Rule 5: Sort by email
    sorted_rows = sorted(email_dict.values(), key=lambda x: x['email'])

    # Write output
    with open('output.json', 'w') as f:
        json.dump(sorted_rows, f)

if __name__ == "__main__":
    main()