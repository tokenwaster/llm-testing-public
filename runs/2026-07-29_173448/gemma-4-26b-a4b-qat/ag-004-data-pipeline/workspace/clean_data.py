import csv
import json
from datetime import datetime

def clean_data(input_file, output_file):
    cleaned_data = []

    with open(input_file, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            email = row.get('email', '').strip()
            signup = row.get('signup', '').strip()
            score_str = row.get('score', '').strip()

            # 1. Drop invalid rows
            if '@' not in email or not email:
                continue
            if not score_str:
                continue
            
            # Try to convert score to int
            try:
                score = int(score_str)
            except ValueError:
                continue

            # 2. Normalize emails
            email = email.lower()

            # 3. Normalize dates
            signup_date = None
            # Try YYYY-MM-DD
            try:
                signup_date = datetime.strptime(signup, '%Y-%m-%d').strftime('%Y-%m-%d')
            except ValueError:
                # Try DD/MM/YYYY
                try:
                    signup_date = datetime.strptime(signup, '%d/%m/%Y').strftime('%Y-%m-%d')
                except ValueError:
                    # If it's neither, we might need to decide what to do.
                    # The problem says "either YYYY-MM-DD or DD/MM/YYYY".
                    # If it's something else, we'll skip it for robustness, 
                    # although the instructions imply these are the only two formats.
                    continue
            
            cleaned_data.append({
                "email": email,
                "signup": signup_date,
                "score": score
            })

    # 4. Deduplicate by email: keep the row with the highest score
    # Use a dictionary to keep track of the best record for each email
    best_records = {}
    for record in cleaned_data:
        email = record['email']
        if email not in best_records or record['score'] > best_records[email]['score']:
            best_records[email] = record

    # Convert back to list
    deduplicated_data = list(best_records.values())

    # 5. Sort the remaining records by email, ascending
    deduplicated_data.sort(key=lambda x: x['email'])

    # Write to output.json
    with open(output_file, mode='w', encoding='utf-8') as jsonfile:
        json.dump(deduplicated_data, jsonfile, indent=4)

if __name__ == "__main__":
    clean_data('data.csv', 'output.json')
