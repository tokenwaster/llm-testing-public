"""Generate the ctx-013 ledger haystack + compute the reference answers.

A long audit log (~60k chars) of transactions across 30 accounts, buried in
distractor prose. Transactions are SETTLED or PENDING; a VOID cancels an earlier
transaction; an AMEND changes an earlier transaction's amount. The settled,
non-voided, amended balance per account drives five derived answers.

Deterministic: a fixed seed, so the prompt and answers are reproducible. Run:
    python tasks-refs/ctx-013-ledger-supersede-64k/generate.py
writes prompt.md next to the task and prints the answers to embed in checker.py.
"""
import random
from pathlib import Path

SEED = 130713
N_ACCT = 30
N_TXN = 640

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
    "corrections are expressed only as explicit VOID or AMEND references.",
    "Note: pending lines are provisional and do not affect settled balances, a "
    "point the training material stresses because it is the usual source of "
    "reconciliation error among new analysts.",
    "The clearing house acknowledged receipt of the daily summary file and "
    "returned the usual hash confirmation within the agreed service window.",
    "Staff rotated the signing keys per the scheduled maintenance policy and "
    "recorded the rotation in the change log without any posting impact.",
    "No manual overrides were applied to the automated posting engine today; "
    "every entry below flowed through the standard validation pipeline.",
]


def build():
    rng = random.Random(SEED)
    accts = [f"ACCT-{i:02d}" for i in range(1, N_ACCT + 1)]
    lines, txns = [], {}
    tid = 0

    def emit(s):
        lines.append(s)

    emit("AUDIT LEDGER — settled-balance reconciliation")
    emit("Rules recap: a SETTLED transaction counts; a PENDING one does not. "
         "A VOID <id> cancels that transaction entirely. An AMEND <id> <amount> "
         "replaces that transaction's amount (only meaningful for a settled, "
         "non-voided transaction). Process strictly in the order listed.")
    emit("")

    settled_ids = []
    for _ in range(N_TXN):
        r = rng.random()
        if r < 0.62:
            tid += 1
            acct = rng.choice(accts)
            amt = rng.choice([1, -1]) * rng.randint(20, 900)
            status = "SETTLED" if rng.random() < 0.72 else "PENDING"
            txns[tid] = {"acct": acct, "amt": amt, "status": status,
                         "void": False}
            if status == "SETTLED":
                settled_ids.append(tid)
            emit(f"[TXN {tid:04d}] {acct} {amt:+d} {status}")
        elif r < 0.80 and settled_ids:
            ref = rng.choice(settled_ids)
            if not txns[ref]["void"]:
                txns[ref]["void"] = True
            emit(f"[VOID {ref:04d}] entry reversed by operations")
        elif settled_ids:
            ref = rng.choice(settled_ids)
            if not txns[ref]["void"]:
                new = rng.choice([1, -1]) * rng.randint(20, 900)
                txns[ref]["amt"] = new
                emit(f"[AMEND {ref:04d} {new:+d}] corrected amount")
        for _ in range(rng.choice([0, 1, 1, 2])):
            emit(rng.choice(FILLER))

    emit("")
    emit("End of ledger. Compute each account's settled balance (settled, "
         "non-voided transactions, using amended amounts), then answer.")

    bal = {a: 0 for a in accts}
    for t in txns.values():
        if t["status"] == "SETTLED" and not t["void"]:
            bal[t["acct"]] += t["amt"]

    ranked = sorted(bal.items(), key=lambda kv: (-kv[1], kv[0]))
    lowest = min(bal.items(), key=lambda kv: (kv[1], kv[0]))
    answers = {
        "HIGHEST_ACCOUNT": ranked[0][0],
        "HIGHEST_BALANCE": ranked[0][1],
        "LOWEST_ACCOUNT": lowest[0],
        "NET_TOTAL": sum(bal.values()),
        "NUM_NEGATIVE": sum(1 for v in bal.values() if v < 0),
    }
    return "\n".join(lines), answers


PROMPT_HEAD = """A long audit ledger follows. Each account's **settled balance**
is the sum of its **SETTLED**, **non-voided** transactions, using **amended**
amounts where an AMEND was applied. PENDING transactions never count. Process the
entries strictly in the order given.

After reading the whole ledger, end your reply with **exactly** these five lines
and nothing after them:

```
HIGHEST_ACCOUNT: <ACCT-NN with the largest settled balance>
HIGHEST_BALANCE: <that balance, integer>
LOWEST_ACCOUNT: <ACCT-NN with the smallest settled balance>
NET_TOTAL: <sum of every account's settled balance, integer>
NUM_NEGATIVE: <how many accounts end with a negative settled balance>
```

If two accounts tie, choose the one whose id sorts first (ACCT-01 before ACCT-02).

--- LEDGER BEGINS ---

"""


def main():
    body, answers = build()
    prompt = PROMPT_HEAD + body + "\n"
    out = Path(__file__).resolve().parents[2] / \
        "tasks/long-context/ctx-013-ledger-supersede-64k/prompt.md"
    out.write_text(prompt, encoding="utf-8")
    print(f"wrote {out} ({len(prompt):,} chars)")
    for k, v in answers.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
