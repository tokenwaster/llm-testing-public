import csv
import json
from datetime import datetime

def clean_data(input_file, output_file):
    records = {}

    with open(input_file, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row['email'].strip()
            signup = row['signup'].strip()
            score_str = row['score'].strip()

            # Rule 1: Drop invalid rows
            if not email or '@' not in email or not score_str:
                continue
            
            try:
                score = int(score_str)
            except ValueError:
                continue

            # Rule 2: Normalize emails to lowercase
            email = email.lower()

            # Rule 3: Normalize dates
            # YYYY-MM-DD or DD/MM/YYYY
            try:
                if '-' in signup:
                    # Assume YYYY-MM-DD
                    signup_dt = datetime.strptime(signup, '%Y-%m-%d')
                elif '/' in signup:
                    # Assume DD/MM/YYYY
                    signup_dt = datetime.strptime(signup, '%d/%m/%Y')
                else:
                    # If it doesn't match either, we might need to handle it or skip
                    # But the prompt says "either YYYY-MM-DD ... or DD/MM/YYYY"
                    continue
                signup_formatted = signup_dt.strftime('%Y-%m-%d')
            except ValueError:
                continue

            # Rule 4: Deduplicate by email (keep highest score)
            new_record = {
                'email': email,
                'signup': signup_formatted,
                'score': score
            }

            if email in records:
                if score > records[email]['score']:
                    records[email] = new_record
            else:
                records[email] = new_record

    # Rule 5: Sort by email ascending
    sorted_records = sorted(records.values(), key=lambda x: x['email'])

    with open(output_file, mode='w', encoding='utf-8') as f:
        json.dump(sorted_records, f, indent=2)

if __name__ == "__main__":
    clean_data('data.csv', 'output.json')
