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
            # signup values are either YYYY-MM-DD or DD/MM/YYYY
            if '/' in signup:
                try:
                    date_obj = datetime.strptime(signup, '%d/%m/%Y')
                    signup = date_obj.strftime('%Y-%m-%d')
                except ValueError:
                    # If it's not in the expected format, we might want to skip or handle it.
                    # The prompt says "are either YYYY-MM-DD or DD/MM/YYYY", so let's assume they are valid if formatted correctly.
                    pass 
            else:
                # Assume YYYY-MM-DD
                pass

            # 4. Deduplicate by email (keep highest score)
            if email in records:
                if score > records[email]['score']:
                    records[email] = {
                        'email': email,
                        'signup': signup,
                        'score': score
                    }
            else:
                records[email] = {
                    'email': email,
                    'signup': signup,
                    'score': score
                }

    # 5. Sort the remaining records by email, ascending
    sorted_records = sorted(records.values(), key=lambda x: x['email'])

    # Write to output.json
    with open(output_file, mode='w', encoding='utf-8') as f:
        json.dump(sorted_records, f, indent=4)

if __name__ == "__main__":
    clean_data('data.csv', 'output.json')
