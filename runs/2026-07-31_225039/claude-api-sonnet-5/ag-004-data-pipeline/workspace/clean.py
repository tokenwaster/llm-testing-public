import csv, json, re

rows = []
with open("data.csv", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        email = (row.get("email") or "").strip()
        signup = (row.get("signup") or "").strip()
        score = (row.get("score") or "").strip()

        if not email or "@" not in email or not score:
            continue

        email = email.lower()

        m = re.match(r"^(\d{2})/(\d{2})/(\d{4})$", signup)
        if m:
            dd, mm, yyyy = m.groups()
            signup = f"{yyyy}-{mm}-{dd}"
        # else assume already YYYY-MM-DD

        score = int(score)

        rows.append({"email": email, "signup": signup, "score": score})

best = {}
for r in rows:
    e = r["email"]
    if e not in best or r["score"] > best[e]["score"]:
        best[e] = r

result = sorted(best.values(), key=lambda r: r["email"])

with open("output.json", "w") as f:
    json.dump(result, f, indent=2)

print(json.dumps(result, indent=2))
