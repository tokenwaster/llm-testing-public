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
                # Store the raw dictionary for processing
                raw_data.append(row)
    except FileNotFoundError:
        print(f"Error: Input file {input_csv_path} not found.")
        return

    cleaned_records = []

    # --- Rule 1: Drop invalid rows ---
    def is_valid(row):
        email = row.get('email', '').strip()
        score = row.get('score', '').strip()
        signup = row.get('signup', '').strip()

        if '@' not in email or not email:
            return False
        if not score:
            return False
        # Assuming 'signup' is always present if the row structure is consistent, 
        # but checking for emptiness just in case.
        if not signup:
             return False
        return True

    valid_data = [row for row in raw_data if is_valid(row)]

    # --- Rule 2 & 3: Normalize emails and dates (and prepare data structure) ---
    processed_records = []
    for row in valid_data:
        record = {
            "email": row['email'].lower(),  # Rule 2: Lowercase email
            "score": int(row['score']),     # Score must be integer for comparison/output
            "signup": row['signup']
        }

        # Rule 3: Normalize dates
        date_str = record["signup"]
        normalized_date = None
        try:
            # Try YYYY-MM-DD (keep as is)
            datetime.strptime(date_str, '%Y-%m-%d')
            normalized_date = date_str
        except ValueError:
            try:
                # Try DD/MM/YYYY (convert)
                dt_obj = datetime.strptime(date_str, '%d/%m/%Y')
                normalized_date = dt_obj.strftime('%Y-%m-%d') # Output format YYYY-MM-DD
            except ValueError:
                # If date parsing fails entirely, we might drop it or handle it based on strict requirements.
                # Assuming valid input formats are guaranteed if they pass Rule 1 checks implicitly.
                pass

        record["signup"] = normalized_date

        processed_records.append(record)


    # --- Rule 4: Deduplicate by email (keep highest score) ---
    # Use a dictionary to store the best record found so far for each email
    best_records = {}
    for record in processed_records:
        email = record["email"]
        score = record["score"]

        if email not in best_records or score > best_records[email]["score"]:
            # Store a copy of the data, ensuring we keep the normalized date and integer score
            best_records[email] = {
                "email": email,
                "signup": record["signup"],
                "score": score
            }

    final_list = list(best_records.values())


    # --- Rule 5: Sort remaining records by email, ascending ---
    final_list.sort(key=lambda x: x['email'])


    # Final output structure check (ensuring keys and types are correct)
    output_data = []
    for record in final_list:
        output_data.append({
            "email": record["email"],
            "signup": record["signup"],
            "score": int(record["score"]) # Ensure score is output as integer type
        })


    # Write to JSON file
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=4)

    print("Data cleaning complete. Results written to output.json")

if __name__ == "__main__":
    clean_data('data.csv', 'output.json')