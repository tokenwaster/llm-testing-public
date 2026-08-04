import random
from pathlib import Path

SEED = 14
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "tasks-staging" / "reasoning" / "rs-014-ledger-amend-chain"

ACCOUNTS = ("AC-118", "AC-204", "AC-377", "AC-451")


def resolve(lines, account):
    amount, live = {}, {}
    owner, kind = {}, {}
    for op in lines:
        tid = op["tid"]
        if op["op"] == "post":
            owner[tid] = op["account"]
            kind[tid] = op["kind"]
            amount[tid] = op["amount"]
            live[tid] = True
        elif op["op"] == "amend":
            amount[tid] = op["amount"]
        elif op["op"] == "void":
            live[tid] = False
        elif op["op"] == "restore":
            live[tid] = True
    total = 0
    for tid, on in live.items():
        if not on or owner.get(tid) != account:
            continue
        total += amount[tid] if kind[tid] == "credit" else -amount[tid]
    return total


def naive_last_state(lines, account):
    amount, live, owner, kind = {}, {}, {}, {}
    for op in lines:
        tid = op["tid"]
        if op["op"] == "post":
            owner[tid], kind[tid] = op["account"], op["kind"]
            amount[tid], live[tid] = op["amount"], True
        elif op["op"] == "void":
            live[tid] = False
    return sum((amount[t] if kind[t] == "credit" else -amount[t])
               for t, on in live.items()
               if on and owner.get(t) == account)


def naive_ignore_restore(lines, account):
    amount, live, owner, kind = {}, {}, {}, {}
    for op in lines:
        tid = op["tid"]
        if op["op"] == "post":
            owner[tid], kind[tid] = op["account"], op["kind"]
            amount[tid], live[tid] = op["amount"], True
        elif op["op"] == "amend":
            amount[tid] = op["amount"]
        elif op["op"] == "void":
            live[tid] = False
    return sum((amount[t] if kind[t] == "credit" else -amount[t])
               for t, on in live.items()
               if on and owner.get(t) == account)


def naive_all_posts(lines, account):
    return sum((op["amount"] if op["kind"] == "credit" else -op["amount"])
               for op in lines
               if op["op"] == "post" and op["account"] == account)


def naive_first_amount(lines, account):
    amount, live, owner, kind = {}, {}, {}, {}
    for op in lines:
        tid = op["tid"]
        if op["op"] == "post":
            owner[tid], kind[tid] = op["account"], op["kind"]
            amount[tid], live[tid] = op["amount"], True
        elif op["op"] == "void":
            live[tid] = False
        elif op["op"] == "restore":
            live[tid] = True
    return sum((amount[t] if kind[t] == "credit" else -amount[t])
               for t, on in live.items()
               if on and owner.get(t) == account)


NAIVE = {
    "ignores amend and restore": naive_last_state,
    "ignores restore": naive_ignore_restore,
    "sums every posting": naive_all_posts,
    "ignores amend": naive_first_amount,
}


def _instance(rng):
    target = ACCOUNTS[0]
    lines, ids = [], []
    n_post = rng.randint(44, 56)
    for i in range(n_post):
        tid = f"T{100 + i * 7 + rng.randint(0, 5)}"
        while tid in ids:
            tid = f"T{100 + rng.randint(0, 120)}"
        ids.append(tid)
        lines.append({"op": "post", "tid": tid,
                      "account": (target if rng.random() < 0.55
                                  else rng.choice(ACCOUNTS[1:])),
                      "kind": rng.choice(("credit", "debit")),
                      "amount": rng.randrange(20, 900)})
    mine = [op["tid"] for op in lines if op["account"] == target]
    tail = []
    for tid in mine:
        if rng.random() < 0.50:
            tail.append({"op": "amend", "tid": tid,
                         "amount": rng.randrange(20, 900)})
        if rng.random() < 0.50:
            tail.append({"op": "void", "tid": tid})
            if rng.random() < 0.55:
                tail.append({"op": "restore", "tid": tid})
        if rng.random() < 0.30:
            tail.append({"op": "amend", "tid": tid,
                         "amount": rng.randrange(20, 900)})
    for tid in [op["tid"] for op in lines if op["account"] != target][:8]:
        tail.append({"op": rng.choice(("void", "amend")), "tid": tid,
                     "amount": rng.randrange(20, 900)})
    rng.shuffle(tail)
    return lines + tail, target


def build(seed: int):
    rng = random.Random(seed)
    for _ in range(4000):
        lines, target = _instance(rng)
        truth = resolve(lines, target)
        traps = {k: f(lines, target) for k, f in NAIVE.items()}
        if any(v == truth for v in traps.values()):
            continue
        if len(set(traps.values())) < 3:
            continue
        if abs(truth) < 50 or truth == 0:
            continue
        if sum(1 for op in lines if op["op"] == "restore") < 5:
            continue
        seen_amend = set()
        double = 0
        for op in lines:
            if op["op"] == "amend":
                double += op["tid"] in seen_amend
                seen_amend.add(op["tid"])
        if double < 3:
            continue
        if len({op["tid"] for op in lines if op["op"] == "post"
                and op["account"] == target}) < 24:
            continue
        return {"lines": lines, "target": target, "answer": truth,
                "traps": traps}
    raise SystemError("no instance defeated every naive strategy")


WORD = {"post": "POST", "amend": "AMEND", "void": "VOID",
        "restore": "RESTORE"}


def render(d) -> str:
    out = []
    for op in d["lines"]:
        if op["op"] == "post":
            out.append(f"POST    {op['tid']} | {op['account']} | "
                       f"{op['kind']} {op['amount']}")
        elif op["op"] == "amend":
            out.append(f"AMEND   {op['tid']} | amount := {op['amount']}")
        else:
            out.append(f"{WORD[op['op']]:<7s} {op['tid']}")
    return "\n".join(out)


PROMPT = """Below is an append-only audit log for a set of accounts. Apply the
entries **in the order written**, top to bottom.

- `POST <id> | <account> | credit N` adds N to that account. `debit N`
  subtracts N. A posting starts out counting.
- `AMEND <id> | amount := M` replaces that entry's amount with M. The account
  and the credit/debit direction never change. An entry may be amended more
  than once; the last amendment before the end is the one that counts.
- `VOID <id>` stops that entry counting.
- `RESTORE <id>` makes it count again. A restored entry keeps whatever amount
  it has at that moment, and it can be voided again afterwards.

An entry counts towards the final balance only if the **last** `VOID` or
`RESTORE` affecting it is a `RESTORE`, or if it was never voided at all.

What is the final balance of **{target}**? Give the integer; it may be
negative.

--- BEGIN LOG ---
{log}
--- END LOG ---
"""

META = """id: rs-014-ledger-amend-chain
category: reasoning
tier: 1
title: Amend, void, restore — a ledger that fights scanning
timeout_s: 900
max_retries: 1
scoring:
  type: answer
  answer: "{answer}"
  tolerance: 0
  match: numeric
"""


def write(out: Path, seed: int) -> dict:
    d = build(seed)
    out.mkdir(parents=True, exist_ok=True)
    (out / "prompt.md").write_text(
        PROMPT.format(target=d["target"], log=render(d)), encoding="utf-8")
    (out / "meta.yaml").write_text(META.format(answer=d["answer"]),
                                   encoding="utf-8")
    return d


def main() -> None:
    d = write(OUT, SEED)
    print(f"seed {SEED}: {len(d['lines'])} log lines, target {d['target']}")
    print(f"  answer {d['answer']}")
    for k, v in d["traps"].items():
        print(f"  trap [{k}] -> {v}")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
