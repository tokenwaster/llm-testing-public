import json, datetime

def clean_csv(file_path):
    emails = []
    
    for line in file_path:
        email, signup, score = line.strip().split(',')
        
        if not email or not signup or not score:
            continue  # Skip invalid rows
            
        email_lower = email.lower()
        signup_lower = signup.lower()  
        
        # Validate email format contains both @ and .
        if '@' in email_lower and '.' in email_lower:
            date_str = datetime.strptime(signup, '%b %d/%Y')
            formatted_date = date_str.strftime('%Y-%m-%d')
            
            emails.append({
                "email": email_lower,
                "signup": formatted_date,
                "score": int(score) if score.strip() != '' else 0
            })
    
    return sorted(set(emails.items()), key=lambda x: x[0])

if __name__ == '__main__':
    cleaned = clean_csv("data.csv")
    output = []
    
    for email, signup, score in cleaned:
        if len(email) > 0 and signup is not None and score is not None:
            output.append({
                "email": email,
                "signup": signup,
                "score": int(score)
            })
            
print(f"Output: {output}")

with open('solution.json', 'w') as f_out:
    json.dump(output, f_out, ensure_ascii=False))

All valid records have been collected and written to solution.json