import csv, json, os

here = os.path.dirname(os.path.abspath(__file__))

def norm_date(s):
    s = s.strip()
    if "/" in s:
        d, m, y = s.split("/")
        return f"{y}-{m.zfill(2)}-{d.zfill(2)}"
    return s

rows = []
with open(os.path.join(here, "data.csv"), newline="") as f:
    for r in csv.DictReader(f):
        email = r["email"].strip()
        score = r["score"].strip()
        # 1. drop invalid
        if "@" not in email or email == "" or score == "":
            continue
        # 2. normalize email
        email = email.lower()
        # 3. normalize date
        signup = norm_date(r["signup"])
        rows.append({"email": email, "signup": signup, "score": int(score)})

# 4. dedup by email, keep highest score
best = {}
for row in rows:
    e = row["email"]
    if e not in best or row["score"] > best[e]["score"]:
        best[e] = row

# 5. sort by email
result = sorted(best.values(), key=lambda x: x["email"])

with open(os.path.join(here, "output.json"), "w") as f:
    json.dump(result, f, indent=2)

print(json.dumps(result, indent=2))
