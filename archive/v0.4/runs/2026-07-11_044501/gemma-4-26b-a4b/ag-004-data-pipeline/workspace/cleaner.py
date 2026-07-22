import csv
import json
from datetime import datetime

def clean_data(input_file, output_file):
    records = {}

    with open(input_file, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row['email'].strip()
            signup_str = row['signup'].strip()
            score_str = row.get('score', '').strip()

            # 1. Drop invalid rows
            if not email or '@' not in email:
                continue
            if not score_str:
                continue
            
            try:
                score = int(score_str)
            except ValueError:
                continue

            # 2. Normalize emails to lowercase
            email = email.lower()

            # 3. Normalize dates
            signup_date = None
            for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
                try:
                    signup_date = datetime.strptime(signup_str, fmt).strftime("%Y-%m-%d")
                    break
                except ValueError:
                    continue
            
            if signup_date is None:
                # If date format is unrecognized, we might want to skip or handle it. 
                # The prompt says "are either YYYY-MM-DD or DD/MM/YYYY".
                # Let's assume if it doesn't match these, it's invalid for our purposes.
                continue

            # 4. Deduplicate by email: keep highest score
            if email in records:
                if score > records[email]['score']:
                    records[email] = {
                        "email": email,
                        "signup": signup_date,
                        "score": score
                    }
            else:
                records[email] = {
                    "email": email,
                    "signup": signup_date,
                    "score": score
                }

    # 5. Sort by email ascending
    sorted_records = sorted(records.values(), key=lambda x: x['email'])

    with open(output_file, mode='w', encoding='utf-8') as f:
        json.dump(sorted_records, f, indent=2)

if __name__ == "__main__":
    clean_data('data.csv', 'output.json')
