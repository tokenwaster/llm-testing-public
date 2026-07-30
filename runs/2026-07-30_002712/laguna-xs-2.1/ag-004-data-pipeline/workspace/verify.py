import json

with open('output.json', 'r') as f:
    data = json.load(f)

print("Number of records:", len(data))
print("\nKeys in each record:")
for i, d in enumerate(data):
    print(f"Record {i+1}: keys = {list(d.keys())}")
    
print("\nTypes verification:")
for i, d in enumerate(data):
    email_type = type(d['email']).__name__
    signup_type = type(d['signup']).__name__
    score_type = type(d['score']).__name__
    print(f"Record {i+1}: email={email_type}, signup={signup_type}, score={score_type}")

print("\nAll records:")
for d in data:
    print(d)