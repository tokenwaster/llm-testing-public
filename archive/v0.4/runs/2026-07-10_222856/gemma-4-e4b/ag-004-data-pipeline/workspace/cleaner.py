import csv
import json
from datetime import datetime
from collections import defaultdict

def clean_data(csv_path, output_path):
    """
    Cleans user signup data according to specified rules and writes the result to JSON.
    Uses only standard Python libraries (csv, json, datetime).
    """
    records = []
    try:
        with open(csv_path, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Store the raw row data for processing
                records.append(row)
    except FileNotFoundError:
        print(f"Error: {csv_path} not found.")
        return

    # --- Cleaning Rules ---

    # 1. Drop invalid rows
    valid_records = []
    for row in records:
        email = row.get('email', '').strip()
        score_str = row.get('score', '').strip()
        signup_date = row.get('signup', '').strip()

        # Check validity criteria:
        # a) email contains no '@' OR b) email is empty OR c) score is empty
        is_invalid = (
            '@' not in email or 
            not email or 
            not score_str
        )
        if not is_invalid:
            valid_records.append(row)

    print(f"Dropped {len(records) - len(valid_records)} invalid rows.")


    # 2. Normalize emails to lowercase & 3. Normalize dates
    processed_data = []
    for row in valid_records:
        email = row['email'].lower()
        score = int(row['score']) # Assuming score is always convertible to int after validation
        signup_date = row['signup']

        # Date normalization logic
        normalized_date = None
        if '/' in signup_date and len(signup_date.split('/')[0]) == 2:
            try:
                day, month, year = map(int, signup_date.split('/'))
                normalized_date = f"{year:04d}-{month:02d}-{day:02d}"
            except ValueError:
                pass # Keep it None if conversion fails

        elif '-' in signup_date and len(signup_date.split('-')[0]) == 4:
             # Already YYYY-MM-DD format, keep as is
             normalized_date = signup_date
        else:
            # Fallback for unexpected formats (shouldn't happen based on prompt)
            pass

        processed_data.append({
            'email': email,
            'signup': normalized_date,
            'score': score
        })


    # 4. Deduplicate by email: keep only the row with the highest score.
    # Use a dictionary to store the best record found so far for each email.
    best_records = {} # Key: email, Value: {'signup': date, 'score': int}

    for item in processed_data:
        email = item['email']
        current_score = item['score']
        
        if email not in best_records or current_score > best_records[email]['score']:
            best_records[email] = {
                'signup': item['signup'],
                'score': current_score
            }

    # Convert the dictionary values back into a list of records, adding the email key
    deduplicated_list = []
    for email, data in best_records.items():
        deduplicated_list.append({
            "email": email,
            "signup": data['signup'],
            "score": data['score']
        })

    print(f"Deduplicated records: {len(deduplicated_list)}")


    # 5. Sort the remaining records by email, ascending.
    final_records = sorted(deduplicated_list, key=lambda x: x['email'])

    # --- Final Formatting and Output ---

    # Write the result to output.json
    with open(output_path, 'w') as f:
        json.dump(final_records, f, indent=4)

    print(f"Successfully wrote cleaned data to {output_path}")


if __name__ == "__main__":
    clean_data('data.csv', 'output.json')