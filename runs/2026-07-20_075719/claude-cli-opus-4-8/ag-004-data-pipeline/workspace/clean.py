import csv, json, re

rows = []
with open("data.csv", newline="") as f:
    for r in csv.DictReader(f):
        email = (r["email"] or "").strip()
        score = (r["score"] or "").strip()
        signup = (r["signup"] or "").strip()
        # rule 1: drop invalid
        if "@" not in email or email == "" or score == "":
            continue
        # rule 2: lowercase email
        email = email.lower()
        # rule 3: normalize date
        if re.fullmatch(r"\d{2}/\d{2}/\d{4}", signup):
            d, m, y = signup.split("/")
            signup = f"{y}-{m}-{d}"
        rows.append({"email": email, "signup": signup, "score": int(score)})

# rule 4: dedup by email, keep highest score
best = {}
for row in rows:
    e = row["email"]
    if e not in best or row["score"] > best[e]["score"]:
        best[e] = row

# rule 5: sort by email ascending
result = sorted(best.values(), key=lambda x: x["email"])

with open("output.json", "w") as f:
    json.dump(result, f, indent=2)

print(json.dumps(result, indent=2))
