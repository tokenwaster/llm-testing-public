import csv
import json
from datetime import datetime

def clean_data(input_csv_path, output_json_path):
    """
    Cleans user signup data according to specified rules and writes the result to a JSON file.
    """
    cleaned_records = []

    # 1. Read CSV and apply initial filtering/cleaning steps (Rules 1, 2, 3)
    try:
        with open(input_csv_path, mode='r', newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            # Assuming the CSV headers match the expected fields: email, signup, score
            
            for row in reader:
                record = {}
                email = row.get('email', '').strip()
                signup_raw = row.get('signup', '').strip()
                score_raw = row.get('score', '').strip()

                # Rule 1: Drop invalid rows
                if '@' not in email or not email or not score_raw:
                    continue
                
                try:
                    score = int(float(score_raw)) # Handle potential float representation of integers
                except ValueError:
                    # If score cannot be converted to integer, treat as invalid (though Rule 1 only checks for empty)
                    # Given the prompt implies scores are present if not empty, we'll assume valid conversion is possible if non-empty.
                    continue

                # Rule 2: Normalize emails to lowercase
                normalized_email = email.lower()

                # Rule 3: Normalize dates
                signup_date = None
                try:
                    if '-' in signup_raw and len(signup_raw) == 10: # YYYY-MM-DD format check (simple heuristic)
                        # Assume it's already YYYY-MM-DD
                        datetime.strptime(signup_raw, '%Y-%m-%d')
                        signup_date = signup_raw
                    elif '/' in signup_raw and len(signup_raw) == 10: # DD/MM/YYYY format check (simple heuristic)
                        # Convert DD/MM/YYYY to YYYY-MM-DD
                        dt_obj = datetime.strptime(signup_raw, '%d/%m/%Y')
                        signup_date = dt_obj.strftime('%Y-%m-%d')
                    else:
                        # Skip if date format is unrecognized and not empty (though Rule 1 handles emptiness)
                        continue

                except ValueError:
                    # If date parsing fails, skip the row
                    continue


                record = {
                    "email": normalized_email,
                    "signup": signup_date,
                    "score": score
                }
                cleaned_records.append(record)

    except FileNotFoundError:
        print(f"Error: Input file {input_csv_path} not found.")
        return []


    # Rule 4: Deduplicate by email (keep row with highest score)
    # Use a dictionary to store the best record for each email
    best_records = {}
    for record in cleaned_records:
        email = record['email']
        score = record['score']
        
        if email not in best_records or score > best_records[email]['score']:
            best_records[email] = record

    final_list = list(best_records.values())


    # Rule 5: Sort the remaining records by email, ascending
    sorted_records = sorted(final_list, key=lambda x: x['email'])

    # Final structure check and output preparation
    output_data = []
    for record in sorted_records:
        output_data.append({
            "email": record["email"],
            "signup": record["signup"],
            "score": int(record["score"]) # Ensure score is written as integer type if possible
        })

    # Write to JSON file
    with open(output_json_path, 'w', encoding='utf-8') as outfile:
        json.dump(output_data, outfile, indent=4)
    
    print("Cleaning complete. Results written to output.json")


if __name__ == "__main__":
    clean_data('data.csv', 'output.json')