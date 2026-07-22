import csv
import json
from datetime import datetime

def clean_data(input_csv_path, output_json_path):
    """
    Cleans user signup data according to specified rules and saves it to a JSON file.
    """
    raw_data = []
    try:
        with open(input_csv_path, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Assuming the CSV headers match expected fields like 'email', 'signup', 'score'
                raw_data.append(row)
    except FileNotFoundError:
        print(f"Error: Input file {input_csv_path} not found.")
        return

    # --- Rule 1: Drop invalid rows ---
    valid_rows = []
    for row in raw_data:
        email = row.get('email', '').strip()
        score = row.get('score', '').strip()
        signup = row.get('signup', '').strip()

        # Check validity conditions
        is_invalid = (
            '@' not in email or 
            not email or 
            not score
        )
        if not is_invalid:
            valid_rows.append(row)

    # --- Rule 2: Normalize emails to lowercase ---
    for row in valid_rows:
        row['email'] = row['email'].lower().strip()

    # --- Rule 3: Normalize dates (YYYY-MM-DD or DD/MM/YYYY -> YYYY-MM-DD) ---
    def normalize_date(date_str):
        if not date_str:
            return None
        
        # Check for YYYY-MM-DD format
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return date_str # Already correct format
        except ValueError:
            pass

        # Check for DD/MM/YYYY format
        try:
            dt_obj = datetime.strptime(date_str, '%d/%m/%Y')
            return dt_obj.strftime('%Y-%m-%d') # Convert to YYYY-MM-DD
        except ValueError:
            # If neither format matches, we might treat it as invalid or keep original if necessary, 
            # but based on rules, we assume valid inputs are one of the two formats.
            return None

    for row in valid_rows:
        row['signup'] = normalize_date(row['signup'])


    # --- Rule 4: Deduplicate by email (keep highest score) ---
    email_scores = {} # Key: email, Value: {'score': int, 'signup': str}

    for row in valid_rows:
        try:
            current_score = int(row['score'])
        except ValueError:
            # Should not happen if Rule 1 passed, but good practice.
            continue

        email = row['email']
        signup = row['signup']
        
        if email not in email_scores or current_score > email_scores[email]['score']:
            email_scores[email] = {
                'email': email,
                'signup': signup,
                'score': current_score
            }

    # Collect the final records
    deduplicated_records = list(email_scores.values())

    # --- Rule 5: Sort remaining records by email, ascending ---
    sorted_records = sorted(deduplicated_records, key=lambda x: x['email'])

    # Final formatting and writing to JSON
    final_output = []
    for record in sorted_records:
        final_output.append({
            "email": record["email"],
            "signup": record["signup"],
            "score": int(record["score"]) # Ensure score is integer type for JSON
        })

    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(final_output, f, indent=4)

    print("Data cleaning complete. Results written to output.json")


if __name__ == "__main__":
    clean_data('data.csv', 'output.json')