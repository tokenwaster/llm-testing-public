import csv
from datetime import datetime
import json

def normalize_date(date_str):
    """Converts date string from DD/MM/YYYY or keeps YYYY-MM-DD."""
    if not date_str:
        return None
    date_str = str(date_str).strip()
    
    # 1. Check for DD/MM/YYYY format
    try:
        dt = datetime.strptime(date_str, '%d/%m/%Y')
        return dt.strftime('%Y-%m-%d') # Output format is YYYY-MM-DD
    except ValueError:
        pass

    # 2. Check for YYYY-MM-DD format (keep as is)
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return date_str # Already correct format
    except ValueError:
        # If neither format matches the expected input formats
        return None

def clean_data():
    """Reads data from data.csv, applies cleaning rules, and returns a list of final records."""
    
    records = []
    try:
        with open('data.csv', mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                record = {
                    'email': row['email'], 
                    'signup': row['signup'], 
                    'score': row['score']
                }
                records.append(record)
    except FileNotFoundError:
        print("Error: data.csv not found.")
        return []

    # --- Rule 1: Drop invalid rows ---
    cleaned_records = []
    for record in records:
        email = str(record['email']).strip() if record.get('email') else ""
        score = str(record['score']).strip() if record.get('score') else ""
        signup = str(record['signup']).strip() if record.get('signup') else ""

        # Invalid if: email contains no '@', email is empty, or score is empty.
        if ('@' in email and 
            email != '' and 
            score != ''):
                cleaned_records.append(record)
    print(f"Rule 1 applied: Processed {len(records)} rows, retained {len(cleaned_records)} after dropping invalid rows.")


    # --- Rule 2 & 3: Normalize emails and dates, and prepare for deduplication ---
    processed_records = []
    for record in cleaned_records:
        email = str(record['email']).strip().lower() # Rule 2: Lowercase email
        signup = normalize_date(record['signup']) # Rule 3: Normalize date
        score = int(float(record['score'])) if record['score'] else None # Convert score to usable integer type

        # Only keep rows where date normalization succeeded and score is valid
        if signup and score is not None:
            processed_records.append({
                'email': email,
                'signup': signup,
                'score': score
            })
    print(f"Rule 2 & 3 applied: Successfully parsed dates/emails for {len(processed_records)} records.")


    # --- Rule 4: Deduplicate by email (keep highest score) ---
    # Key: email, Value: dict containing the record data
    best_records = {}

    for record in processed_records:
        email = record['email']
        score = record['score']
        
        if email not in best_records or score > best_records[email]['score']:
            best_records[email] = {
                "email": record['email'], 
                "signup": record['signup'], 
                "score": record['score']
            }

    final_list = list(best_records.values())
    print(f"Rule 4 applied: Deduplicated by email, remaining unique records: {len(final_list)}.")


    # --- Rule 5 & Output Formatting: Sort and format for JSON ---
    # Sorting by email ascending (Rule 5)
    final_list.sort(key=lambda x: x['email'])

    output_data = final_list # The structure is already correct: {"email": str, "signup": str, "score": int}
    return output_data

def main():
    """Main function to run the cleaning process and write to output.json."""
    output_records = clean_data()

    # Write the result to output.json
    try:
        with open('output.json', 'w') as f:
            json.dump(output_records, f, indent=4)
        print("\nSuccessfully wrote cleaned data to output.json")
    except Exception as e:
        print(f"Error writing file: {e}")

if __name__ == "__main__":
    main()