import csv
import json
from datetime import datetime
from collections import defaultdict

def normalize_date(date_str):
    """Converts date string from DD/MM/YYYY or YYYY-MM-DD to YYYY-MM-DD."""
    if not date_str:
        return None
    date_str = str(date_str).strip()

    # Check for DD/MM/YYYY format (contains '/')
    if '/' in date_str and len(date_str.split('/')[0]) <= 2 and len(date_str.split('/')[1]) <= 2:
        try:
            day, month, year = map(int, date_str.split('/'))
            return f"{year:04d}-{month:02d}-{day:02d}"
        except ValueError:
            pass # Failed conversion

    # Check for YYYY-MM-DD format (contains '-')
    if '-' in date_str and len(date_str.split('-')[0]) == 4:
        return date_str

    return None # Return None if format is unrecognized or invalid

def clean_data(csv_path, json_path):
    """Reads messy CSV data, cleans it according to rules, and writes the result to JSON."""
    records = []
    
    # 1. Read all records
    try:
        with open(csv_path, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                record = {k.strip(): v.strip() for k, v in row.items()}
                records.append(record)
    except FileNotFoundError:
        print(f"Error: {csv_path} not found.")
        return

    # --- 1. Drop invalid rows ---
    valid_records = []
    for record in records:
        email = record.get('email', '')
        score_str = record.get('score', '')
        signup_str = record.get('signup', '')

        is_invalid = False
        # Check 1: email contains no '@' or is empty
        if '@' not in email or not email:
            is_invalid = True
        # Check 2: score is empty (after stripping whitespace)
        elif not score_str.strip():
            is_invalid = True
        # Note: The prompt implies 'signup' being empty might be invalid, but the rules only list email/score checks for dropping rows. We proceed assuming we keep records with missing signup dates if other criteria pass.

        if not is_invalid:
            valid_records.append(record)

    # --- 2. Normalize emails to lowercase & Prepare data structure ---
    processed_data = []
    for record in valid_records:
        email = str(record['email']).lower()
        score = int(float(record['score'])) # Convert score to integer, assuming it's always convertible after step 1 filtering
        signup = normalize_date(record.get('signup', ''))
        
        processed_data.append({
            "email": email,
            "signup": signup,
            "score": score
        })

    # --- 3. Deduplicate by email: keep row with highest score ---
    # Use a dictionary to store the best record found so far for each email
    best_records = {} # Key: email, Value: {record}
    for record in processed_data:
        email = record['email']
        score = record['score']
        
        if email not in best_records or score > best_records[email]['score']:
            # Store a copy of the record to avoid mutation issues
            best_records[email] = {
                "email": record["email"],
                "signup": record["signup"],
                "score": record["score"]
            }

    final_list = list(best_records.values())

    # --- 4. Sort remaining records by email, ascending ---
    final_list.sort(key=lambda x: x['email'])

    # --- 5. Write the result to output.json ---
    with open(json_path, 'w') as f:
        json.dump(final_list, f, indent=4)

    print("Data cleaning complete. Output written to output.json")


if __name__ == "__main__":
    clean_data('data.csv', 'output.json')