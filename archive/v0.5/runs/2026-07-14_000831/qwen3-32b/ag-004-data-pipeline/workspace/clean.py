import csv
import json
from datetime import datetime

def normalize_date(date_str):
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        # Try DD/MM/YYYY format
        parts = date_str.split('/')
        if len(parts) != 3:
            raise ValueError(f"Invalid date format: {date_str}")
        day, month, year = map(int, parts)
        dt = datetime(year, month, day)
    return dt.strftime("%Y-%m-%d")

def main():
    # Read CSV
    with open('data.csv', 'r') as f:
        reader = csv.DictReader(f)
        data = [row for row in reader]

    valid_rows = []
    for row in data:
        email = row.get('email', '').strip()
        if not email or '@' not in email:
            continue
        score_str = row.get('score', '').strip()
        if not score_str:
            continue
        try:
            score = int(score_str)
        except ValueError:
            continue

        normalized_email = email.lower()
        signup_date = row.get('signup', '').strip()

        # Normalize date
        try:
            normalized_date = normalize_date(signup_date)
        except ValueError:
            # Invalid date, skip this row?
            continue

        valid_rows.append({
            'email': normalized_email,
            'signup': normalized_date,
            'score': score,
        })

    # Deduplicate by email, keeping highest score
    email_dict = {}
    for row in valid_rows:
        email = row['email']
        if (email not in email_dict or 
            row['score'] > email_dict[email]['score']):
            email_dict[email] = row

    unique_rows = sorted(email_dict.values(), key=lambda x: x['email'])

    # Write to output.json
    with open('output.json', 'w') as f:
        json.dump(unique_rows, f)

if __name__ == "__main__":
    main()