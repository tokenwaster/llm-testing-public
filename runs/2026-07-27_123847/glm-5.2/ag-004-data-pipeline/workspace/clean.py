import csv
import json

rows = []
with open("data.csv", newline="") as f:
    reader = csv.DictReader(f)
    for r in reader:
        email = (r["email"] or "").strip()
        score_raw = (r["score"] or "").strip()
        signup = (r["signup"] or "").strip()

        # 1. Drop invalid rows
        if email == "" or "@" not in email or score_raw == "":
            continue

        # 2. Normalize emails
        email = email.lower()

        # 3. Normalize dates
        if "/" in signup:
            dd, mm, yyyy = signup.split("/")
            signup = f"{yyyy}-{int(mm):02d}-{int(dd):02d}"
        # else assume already YYYY-MM-DD; validate format loosely
        else:
            parts = signup.split("-")
            signup = f"{int(parts[0]):04d}-{int(parts[1]):02d}-{int(parts[2]):02d}"

        score = int(score_raw)

        rows.append({"email": email, "signup": signup, "score": score})

# 4. Deduplicate by email: keep highest score
best = {}
for r in rows:
    e = r["email"]
    if e not in best or r["score"] > best[e]["score"]:
        best[e] = r

result = list(best.values())

# 5. Sort by email ascending
result.sort(key=lambda x: x["email"])

with open("output.json", "w") as f:
    json.dump(result, f, indent=2)

print(json.dumps(result, indent=2))
