import csv
import json
import re
from pathlib import Path

HERE = Path(__file__).parent
DMY = re.compile(r"^(\d{2})/(\d{2})/(\d{4})$")
YMD = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def normalize_date(value):
    value = value.strip()
    if YMD.match(value):
        return value
    m = DMY.match(value)
    if m:
        day, month, year = m.groups()
        return f"{year}-{month}-{day}"
    raise ValueError(f"unrecognized date: {value!r}")


best = {}
with (HERE / "data.csv").open(newline="", encoding="utf-8") as fh:
    for row in csv.DictReader(fh):
        email = (row.get("email") or "").strip()
        score = (row.get("score") or "").strip()
        if not email or "@" not in email or not score:
            continue
        email = email.lower()
        record = {
            "email": email,
            "signup": normalize_date(row.get("signup") or ""),
            "score": int(score),
        }
        if email not in best or record["score"] > best[email]["score"]:
            best[email] = record

records = sorted(best.values(), key=lambda r: r["email"])
(HERE / "output.json").write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
print(f"{len(records)} records written")
