"""Generator + reference for ctx-012-aggregate-reversals-32k (v0.6 long-context).

Numeric aggregation that punishes skimming: sum the SETTLED movements for ONE
account among a long ledger, where (a) most lines are other accounts, and (b)
PENDING and REVERSED lines look identical to settled ones but must be excluded.
Answer computed by construction.
"""

import random
from pathlib import Path

SEED = 20260716
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "tasks-staging" / "long-context" / "ctx-012-aggregate-reversals-32k"


def build():
    rng = random.Random(SEED)
    accounts = [f"AC-{n:04d}" for n in rng.sample(range(1000, 9999), 25)]
    target = accounts[0]

    lines, settled_target = [], 0
    n = 0
    while n < 1300:
        acct = rng.choice(accounts)
        amt = rng.randint(1, 999)
        sign = rng.choice([1, -1])
        state = rng.choices(["SETTLED", "PENDING", "REVERSED"],
                            weights=[6, 2, 2])[0]
        verb = "credit" if sign > 0 else "debit"
        lines.append(f"txn {n:04d} | {acct} | {verb} {amt} | {state}")
        if acct == target and state == "SETTLED":
            settled_target += sign * amt
        n += 1
    rng.shuffle(lines)
    body = "\n".join(lines)

    prompt = (
        "You are given a long, unordered transaction ledger. Each line has a "
        "transaction id, an account, a movement (`credit N` adds N, `debit N` "
        "subtracts N), and a STATE.\n\n"
        f"Compute the net balance of account **{target}** counting ONLY lines "
        f"whose state is `SETTLED`. Lines marked `PENDING` or `REVERSED`, and "
        f"all lines for other accounts, must be excluded.\n\n"
        "Reply with the net integer (it may be negative), e.g. `-42`.\n\n"
        "--- BEGIN LEDGER ---\n" + body + "\n--- END LEDGER ---\n"
    )
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "prompt.md").write_text(prompt, encoding="utf-8")
    (OUT / "meta.yaml").write_text(
        "id: ctx-012-aggregate-reversals-32k\n"
        "category: long-context\n"
        "tier: 1\n"
        "title: Settled-only balance under pending/reversed noise @ 32k\n"
        "timeout_s: 600\n"
        "max_retries: 1\n"
        "scoring:\n"
        "  type: answer\n"
        f"  answer: \"{settled_target}\"\n"
        "  match: numeric\n"
        "  tolerance: 0\n", encoding="utf-8")
    return target, settled_target, len(lines), prompt


if __name__ == "__main__":
    target, ans, n, prompt = build()
    print(f"wrote {OUT}")
    print(f"target={target}  answer(net settled)={ans}  lines={n}  ~tokens={len(prompt)//4:,}")
