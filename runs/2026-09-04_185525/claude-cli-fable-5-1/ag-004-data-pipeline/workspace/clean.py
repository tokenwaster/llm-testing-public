import csv
import json
import re
from pathlib import Path

here = Path(__file__).parent
rows = list(csv.DictReader((here / "data.csv").open(newline="", encoding="utf-8")))

best = {}
for r in rows:
    email = (r.get("email") or "").strip()
    score = (r.get("score") or "").strip()
    if not email or "@" not in email or not score:
        continue
    email = email.lower()
    signup = (r.get("signup") or "").strip()
    m = re.fullmatch(r"(\d{2})/(\d{2})/(\d{4})", signup)
    if m:
        d, mo, y = m.groups()
        signup = f"{y}-{mo}-{d}"
    score = int(score)
    if email not in best or score > best[email]["score"]:
        best[email] = {"email": email, "signup": signup, "score": score}

out = sorted(best.values(), key=lambda x: x["email"])
(here / "output.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
print(json.dumps(out, indent=2))
