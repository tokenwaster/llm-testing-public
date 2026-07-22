import csv, json

rows = []
with open("data.csv", newline="") as f:
    for r in csv.DictReader(f):
        email = (r["email"] or "").strip()
        signup = (r["signup"] or "").strip()
        score = (r["score"] or "").strip()

        # 1. Drop invalid rows
        if "@" not in email or email == "" or score == "":
            continue

        # 2. Normalize email
        email = email.lower()

        # 3. Normalize date
        if "/" in signup:
            d, m, y = signup.split("/")
            signup = f"{y}-{m}-{d}"

        rows.append({"email": email, "signup": signup, "score": int(score)})

# 4. Deduplicate by email, keeping highest score
best = {}
for row in rows:
    e = row["email"]
    if e not in best or row["score"] > best[e]["score"]:
        best[e] = row

# 5. Sort by email ascending
out = sorted(best.values(), key=lambda x: x["email"])

with open("output.json", "w") as f:
    json.dump(out, f, indent=2)

print(json.dumps(out, indent=2))
