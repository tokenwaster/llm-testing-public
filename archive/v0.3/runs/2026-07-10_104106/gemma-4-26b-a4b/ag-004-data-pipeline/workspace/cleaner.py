import csv
import json
from datetime import datetime

def clean_data(input_file, output_file):
    rows = []
    with open(input_file, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row.get('email', '').strip()
            signup = row.get('signup', '').strip()
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
            # YYYY-MM-DD or DD/MM/YYYY
            signup_date = None
            for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
                try:
                    signup_date = datetime.strptime(signup, fmt).strftime("%Y-%m-%d")
                    break
                except ValueError:
                    continue
            
            if signup_date is None:
                # If date format doesn't match either, we might want to drop it? 
                # The instructions say "are either YYYY-MM-DD or DD/MM/YYYY".
                # Let's assume if it doesn't match, it's invalid.
                continue

            rows.append({
                "email": email,
                "signup": signup_date,
                "score": score
            })

    # 4. Deduplicate by email: keep highest score
    best_rows = {}
    for row in rows:
        email = row['email']
        if email not in best_rows or row['score'] > best_rows[email]['score']:
            best_rows[email] = row

    # 5. Sort by email ascending
    sorted_rows = sorted(best_rows.values(), key=lambda x: x['email'])

    # Write to output.json
    with open(output_file, mode='w', encoding='utf-8') as f:
        json.dump(sorted_rows, f, indent=2)

if __name__ == "__main__":
    clean_data('data.csv', 'output.json')
