import csv
import json
from datetime import datetime

def clean_data(input_file, output_file):
    data = []
    
    with open(input_file, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row.get('email', '').strip()
            signup = row.get('signup', '').strip()
            score_str = row.get('score', '').strip()

            # 1. Drop invalid rows
            if not email or '@' not in email or not score_str:
                continue
            
            try:
                score = int(score_str)
            except ValueError:
                continue

            # 2. Normalize emails to lowercase
            email = email.lower()

            # 3. Normalize dates
            # signup values are either YYYY-MM-DD or DD/MM/YYYY
            try:
                if '-' in signup:
                    # Assuming YYYY-MM-DD
                    signup_dt = datetime.strptime(signup, '%Y-%m-%d')
                elif '/' in signup:
                    # Assuming DD/MM/YYYY
                    signup_dt = datetime.strptime(signup, '%d/%m/%Y')
                else:
                    continue
                signup_str = signup_dt.strftime('%Y-%m-%d')
            except ValueError:
                continue

            data.append({
                'email': email,
                'signup': signup_str,
                'score': score
            })

    # 4. Deduplicate by email: keep the row with the highest score
    deduplicated = {}
    for entry in data:
        email = entry['email']
        if email not in deduplicated or entry['score'] > deduplicated[email]['score']:
            deduplicated[email] = entry

    # 5. Sort the remaining records by email, ascending
    sorted_data = sorted(deduplicated.values(), key=lambda x: x['email'])

    # Write to output.json
    with open(output_file, mode='w', encoding='utf-8') as f:
        json.dump(sorted_data, f, indent=2)

if __name__ == "__main__":
    clean_data('data.csv', 'output.json')
