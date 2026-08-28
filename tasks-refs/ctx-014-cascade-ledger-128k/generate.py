import random
from pathlib import Path

SEED = 140815
N_ACCT = 36
N_OPS = 850
TASK_ID = "ctx-014-cascade-ledger-128k"
CATEGORY = "long-context"

ALIAS_NAMES = [
    "Harbor Trust", "Meridian Holdings", "Northgate Capital", "Sable & Co",
    "Corvid Partners", "Larkspur Fund", "Tidewater Mutual", "Quillon Group",
    "Aster Logistics", "Bellweather Ltd", "Ironwood Estates", "Juniper Desk",
]

FILLER = [
    "The reconciliation window remained open pending the quarterly review, and "
    "the desk supervisor initialled the interim summary before end of day.",
    "Auditors noted the ledger format complied with the internal standard and "
    "cross-checked a sample of postings against the upstream feed with no drift.",
    "A routine backup of the journal completed without incident overnight; the "
    "restore drill scheduled for the weekend was confirmed on the maintenance "
    "calendar and signed off by the on-call engineer.",
    "The treasury desk flagged nothing unusual in the settlement batch, though "
    "it reminded staff that provisional lines carry no weight until they clear.",
    "Compliance confirmed the counterparties were all previously onboarded and "
    "that no sanctions screening exceptions had been raised during the session.",
    "Ledger entries are recorded in the order they were received; out-of-order "
    "corrections are expressed only as explicit bracketed instructions.",
    "Note: pending lines are provisional and do not affect settled balances, a "
    "point the training material stresses because it is the usual source of "
    "reconciliation error among new analysts.",
    "The clearing house acknowledged receipt of the daily summary file and "
    "returned the usual hash confirmation within the agreed service window.",
    "Staff rotated the signing keys per the scheduled maintenance policy and "
    "recorded the rotation in the change log without any posting impact.",
    "No manual overrides were applied to the automated posting engine today; "
    "every entry below flowed through the standard validation pipeline.",
    "An alias, once declared, is simply another name for the same account; "
    "postings under either name belong to that one account.",
]

DECOYS = [
    "The supervisor considered voiding transaction {id:04d} during the review "
    "but took no action, so that entry stands as recorded.",
    "A draft memo proposed amending transaction {id:04d} to {amt:+d}; the memo "
    "was withdrawn before any instruction was issued.",
    "Operations discussed transferring transaction {id:04d} to {acct}, then "
    "confirmed the original account was correct and left it unchanged.",
    "Someone asked whether transaction {id:04d} had settled; it was still "
    "pending at the time of asking and no instruction followed.",
]


def build():
    rng = random.Random(SEED)
    accts = [f"ACCT-{i:02d}" for i in range(1, N_ACCT + 1)]
    alias_of = {}
    alias_pool = list(ALIAS_NAMES)
    rng.shuffle(alias_pool)
    alias_targets = rng.sample(accts, len(alias_pool))
    pending_alias = list(zip(alias_targets, alias_pool))
    lines, txns = [], {}
    tid = 0

    def emit(s):
        lines.append(s)

    def name_for(acct):
        if acct in alias_of and rng.random() < 0.45:
            return f'"{alias_of[acct]}"'
        return acct

    emit("AUDIT LEDGER v2 — settled-balance reconciliation with cascades")
    emit("Rules recap: a transaction counts toward its account only if it is "
         "SETTLED and not void at the end. VOID <id> marks it void; RESTORE <id> "
         "clears the void mark; AMEND <id> <amount> replaces its amount; SETTLE "
         "<id> changes its status to SETTLED; TRANSFER <id> <account> moves it to "
         "another account; VOID-ALL <account> voids every transaction that "
         "account holds at that moment. Every instruction applies whatever the "
         "transaction's current state. Process strictly in the order listed.")
    emit("")

    ids = []
    for step in range(N_OPS):
        if pending_alias and rng.random() < 0.012 * (1 + step / N_OPS):
            acct, name = pending_alias.pop()
            alias_of[acct] = name
            emit(f'[ALIAS {acct} = "{name}"]')
        r = rng.random()
        if r < 0.50 or not ids:
            tid += 1
            acct = rng.choice(accts)
            amt = rng.choice([1, -1]) * rng.randint(20, 900)
            status = "SETTLED" if rng.random() < 0.66 else "PENDING"
            txns[tid] = {"acct": acct, "amt": amt, "status": status,
                         "void": False}
            ids.append(tid)
            emit(f"[TXN {tid:04d}] {name_for(acct)} {amt:+d} {status}")
        elif r < 0.62:
            ref = rng.choice(ids)
            txns[ref]["void"] = True
            emit(f"[VOID {ref:04d}] entry reversed by operations")
        elif r < 0.70:
            voided = [i for i in ids if txns[i]["void"]]
            ref = rng.choice(voided) if voided and rng.random() < 0.8 \
                else rng.choice(ids)
            txns[ref]["void"] = False
            emit(f"[RESTORE {ref:04d}] reversal withdrawn")
        elif r < 0.80:
            ref = rng.choice(ids)
            new = rng.choice([1, -1]) * rng.randint(20, 900)
            txns[ref]["amt"] = new
            emit(f"[AMEND {ref:04d} {new:+d}] corrected amount")
        elif r < 0.88:
            pend = [i for i in ids if txns[i]["status"] == "PENDING"]
            ref = rng.choice(pend) if pend and rng.random() < 0.85 \
                else rng.choice(ids)
            txns[ref]["status"] = "SETTLED"
            emit(f"[SETTLE {ref:04d}] cleared")
        elif r < 0.965:
            ref = rng.choice(ids)
            dest = rng.choice([a for a in accts if a != txns[ref]["acct"]])
            txns[ref]["acct"] = dest
            emit(f"[TRANSFER {ref:04d} {name_for(dest)}] reassigned")
        else:
            acct = rng.choice(accts)
            for i in ids:
                if txns[i]["acct"] == acct:
                    txns[i]["void"] = True
            emit(f"[VOID-ALL {name_for(acct)}] account frozen pending inquiry")
        if rng.random() < 0.05 and ids:
            d = rng.choice(DECOYS)
            emit(d.format(id=rng.choice(ids),
                          amt=rng.choice([1, -1]) * rng.randint(20, 900),
                          acct=rng.choice(accts)))
        for _ in range(rng.choice([0, 0, 1, 1, 1, 2])):
            emit(rng.choice(FILLER))

    emit("")
    emit("End of ledger. Compute each account's settled balance (transactions "
         "that are SETTLED and not void at the end, at their final amount, in "
         "their final account), then answer.")

    bal = {a: 0 for a in accts}
    active = 0
    for t in txns.values():
        if t["status"] == "SETTLED" and not t["void"]:
            bal[t["acct"]] += t["amt"]
            active += 1
    ranked = sorted(bal.items(), key=lambda kv: (-kv[1], kv[0]))
    lowest = min(bal.items(), key=lambda kv: (kv[1], kv[0]))
    answers = {
        "HIGHEST_ACCOUNT": ranked[0][0],
        "HIGHEST_BALANCE": ranked[0][1],
        "LOWEST_ACCOUNT": lowest[0],
        "NET_TOTAL": sum(bal.values()),
        "NUM_NEGATIVE": sum(1 for v in bal.values() if v < 0),
        "NUM_ACTIVE": active,
    }
    return "\n".join(lines), answers


PROMPT_HEAD = """A long audit ledger follows. A transaction counts toward an
account's **settled balance** only if, after every instruction has been
applied in order, it is **SETTLED** and **not void** — at its **final amount**,
under its **final account**.

Instructions (each applies to the transaction's current state, whatever it is):

- `[TXN id] account amount status` — a new transaction (status SETTLED or PENDING).
- `[VOID id]` — marks it void. `[RESTORE id]` — clears the void mark.
- `[AMEND id amount]` — replaces its amount (void or not, settled or not).
- `[SETTLE id]` — its status becomes SETTLED (a void transaction stays void).
- `[TRANSFER id account]` — moves it to another account.
- `[VOID-ALL account]` — voids every transaction that account holds **at that
  moment**; later transactions and later transfers into it are unaffected.
- `[ALIAS ACCT-NN = "Name"]` — from then on the quoted name refers to that
  account; either form may appear.

Only bracketed lines are instructions. Narrative sentences — including ones
that mention a transaction, an amount or an account — change nothing.

After reading the whole ledger, end your reply with **exactly** these six lines
and nothing after them:

```
HIGHEST_ACCOUNT: <ACCT-NN with the largest settled balance>
HIGHEST_BALANCE: <that balance, integer>
LOWEST_ACCOUNT: <ACCT-NN with the smallest settled balance>
NET_TOTAL: <sum of every account's settled balance, integer>
NUM_NEGATIVE: <how many accounts end with a negative settled balance>
NUM_ACTIVE: <how many transactions count at the end (SETTLED and not void)>
```

Use the ACCT-NN form in the answer even for aliased accounts. If two accounts
tie, choose the one whose id sorts first (ACCT-01 before ACCT-02).

--- LEDGER BEGINS ---

"""


CHECKER_TMPL = '''import pathlib
import re

_TXT = pathlib.Path("response.txt")
TEXT = _TXT.read_text(encoding="utf-8") if _TXT.exists() else ""

EXPECT = {
__EXPECT__}


def _last(label):
    m = re.findall(rf"(?im)^\\s*\\**\\s*{label}\\s*\\**\\s*[:=]\\s*(.+?)\\s*$", TEXT)
    return m[-1].strip() if m else None


def _acct(label):
    v = _last(label)
    if not v:
        return None
    m = re.search(r"ACCT-\\d{2}", v.upper())
    return m.group(0) if m else None


def _int(label):
    v = _last(label)
    if v is None:
        return None
    v = v.replace(",", "").replace("\\u2212", "-")
    xs = re.findall(r"-?\\d+", v)
    return int(xs[0]) if xs else None


def test_highest_account():
    assert _acct("HIGHEST_ACCOUNT") == EXPECT["HIGHEST_ACCOUNT"]


def test_highest_balance():
    assert _int("HIGHEST_BALANCE") == EXPECT["HIGHEST_BALANCE"]


def test_lowest_account():
    assert _acct("LOWEST_ACCOUNT") == EXPECT["LOWEST_ACCOUNT"]


def test_net_total():
    assert _int("NET_TOTAL") == EXPECT["NET_TOTAL"]


def test_num_negative():
    assert _int("NUM_NEGATIVE") == EXPECT["NUM_NEGATIVE"]


def test_num_active():
    assert _int("NUM_ACTIVE") == EXPECT["NUM_ACTIVE"]
'''


def render_checker(answers: dict) -> str:
    rows = "".join(
        f'    "{k}": ' + (f'"{v}"' if isinstance(v, str) else str(v)) + ",\n"
        for k, v in answers.items())
    return CHECKER_TMPL.replace("__EXPECT__", rows)


def main():
    body, answers = build()
    prompt = PROMPT_HEAD + body + "\n"
    root = Path(__file__).resolve().parents[2]
    task_dir = root / "tasks" / CATEGORY / TASK_ID
    if not task_dir.is_dir():
        task_dir = root / "tasks-staging" / CATEGORY / TASK_ID
    task_dir.mkdir(parents=True, exist_ok=True)
    out = task_dir / "prompt.md"
    out.write_text(prompt, encoding="utf-8", newline="\n")
    print(f"wrote {out} ({len(prompt):,} chars)")
    chk = task_dir / "checker.py"
    chk.write_text(render_checker(answers), encoding="utf-8", newline="\n")
    print(f"wrote {chk} (answer key)")
    for k, v in answers.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
