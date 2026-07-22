import csv
import json
from datetime import datetime

def clean_data(input_csv_path, output_json_path):
    """
    Cleans user signup data according to specified rules and saves it to a JSON file.
    """
    raw_data = []
    try:
        with open(input_csv_path, mode='r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                raw_data.append(row)
    except FileNotFoundError:
        print(f"Error: Input file {input_csv_path} not found.")
        return

    # --- Step 1 & 2: Initial Filtering and Normalization (Email) ---
    valid_rows = []
    for row in raw_data:
        email = row.get('email', '').strip()
        signup = row.get('signup', '').strip()
        score_str = row.get('score', '').strip()

        # 1. Drop invalid rows check
        is_invalid = False
        if '@' not in email or not email: # Email contains no @ or is empty
            is_invalid = True
        elif not score_str: # Score is empty
            is_invalid = True
        
        if is_invalid:
            continue

        # 2. Normalize emails to lowercase
        normalized_email = email.lower()
        
        # Convert score to integer for later comparison/storage
        try:
            score = int(float(score_str)) # Use float conversion first in case of '82.0' type data, though input suggests integers
        except ValueError:
            # This should ideally be caught by the empty check above, but good practice to handle it.
            continue 

        valid_rows.append({
            "email": normalized_email,
            "signup": signup,
            "score": score,
            "original_row": row # Keep original for date processing if needed
        })

    # --- Step 3: Normalize Dates ---
    def normalize_date(date_str):
        if not date_str:
            return None
        try:
            # Check YYYY-MM-DD format (e.g., 2024-01-15)
            datetime.strptime(date_str, '%Y-%m-%d')
            return date_str # Already correct format
        except ValueError:
            try:
                # Check DD/MM/YYYY format (e.g., 15/02/2024)
                dt_obj = datetime.strptime(date_str, '%d/%m/%Y')
                return dt_obj.strftime('%Y-%m-%d') # Convert to YYYY-MM-DD
            except ValueError:
                # Handle cases where the date format is neither expected type
                return None

    processed_rows = []
    for row in valid_rows:
        normalized_signup = normalize_date(row['signup'])
        if normalized_signup:
             processed_rows.append({
                "email": row["email"],
                "signup": normalized_signup,
                "score": row["score"]
            })

    # --- Step 4: Deduplicate by email (Keep highest score) ---
    # Use a dictionary to store the best record found so far for each email
    best_records = {}
    for record in processed_rows:
        email = record['email']
        score = record['score']
        
        if email not in best_records or score > best_records[email]['score']:
            best_records[email] = {
                "email": record["email"],
                "signup": record["signup"],
                "score": record["score"]
            }

    final_list = list(best_records.values())

    # --- Step 5: Sort by email, ascending ---
    sorted_list = sorted(final_list, key=lambda x: x['email'])

    # Write the final result to output.json
    with open(output_json_path, 'w') as f:
        json.dump(sorted_list, f, indent=4)

    print("Cleaning complete. Results written to output.json")


if __name__ == "__main__":
    clean_data('data.csv', 'output.json')