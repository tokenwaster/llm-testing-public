import json
from datetime import datetime

def clean_csv(file_path):
    emails = []
    for row in file_path:
        email, signup, score = row.strip().split(',')
        try:
            if email:  # Check if email is not empty
                email_lower = email.lower()
                signup_lower = signup.lower()  
                
                # Validate email format
                if '@' in email_lower and '.' in email_lower:
                    date_str = datetime.strptime(signup, '%b %d/%Y')
                    formatted_date = date_str.strftime('%Y-%m-%d')
                    
                    email_key = email_lower 
                    score_val = int(score)
                    emails.append({
                        "email": email_key,
                        "signup": formatted_date,
                        "score": score_val
                    })
        except:  # Handle any errors
            continue

    return sorted(set(emails.items()), key=lambda x: x[0])

if __name__ == "__main__":
    cleaned = clean_csv("data.csv")
    output = []
    
    for email, signup, score in cleaned:
        if len(email) > 0 and signup is not None and score is not None:
            output.append({"email": email, "signup": signup, "score": score})
            
print(f"Output: {output}")

with open('output.json', 'w') as f_out:
    json.dump(output, f_out)

All valid records have been collected and written to output.json