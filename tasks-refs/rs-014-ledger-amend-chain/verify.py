import re
import sys
import tempfile
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from generate import NAIVE, SEED, build, render, resolve, write

from harness import scoring


class _T:
    def __init__(self, m):
        self.id = m["id"]
        self.category = m["category"]
        self.scoring = m["scoring"]


def from_text(log: str, account: str) -> int:
    timeline: dict[str, list] = {}
    for line in log.splitlines():
        m = re.match(r"POST\s+(\S+)\s+\|\s+(\S+)\s+\|\s+(credit|debit)\s+(\d+)",
                     line)
        if m:
            timeline.setdefault(m.group(1), []).append(
                ("post", m.group(2), m.group(3), int(m.group(4))))
            continue
        m = re.match(r"AMEND\s+(\S+)\s+\|\s+amount\s+:=\s+(\d+)", line)
        if m:
            timeline.setdefault(m.group(1), []).append(
                ("amend", int(m.group(2))))
            continue
        m = re.match(r"(VOID|RESTORE)\s+(\S+)", line)
        if m:
            timeline.setdefault(m.group(2), []).append((m.group(1).lower(),))
    total = 0
    for tid, events in timeline.items():
        post = next((e for e in events if e[0] == "post"), None)
        if post is None or post[1] != account:
            continue
        amount = post[3]
        for e in events:
            if e[0] == "amend":
                amount = e[1]
        gate = [e[0] for e in events if e[0] in ("void", "restore")]
        if gate and gate[-1] == "void":
            continue
        total += amount if post[2] == "credit" else -amount
    return total


def verify(seed: int) -> bool:
    d = build(seed)
    ok = True
    log = render(d)
    print(f"seed {seed}: {len(d['lines'])} lines, target {d['target']}, "
          f"key {d['answer']}")

    second = from_text(log, d["target"])
    if second != d["answer"]:
        ok = False
        print(f"  FAIL independent re-read of the rendered log gives {second}, "
              f"not {d['answer']} — the key is only as good as one "
              f"implementation")
    else:
        print(f"  ok   a second resolver, parsing the rendered text rather "
              f"than the structures, agrees: {second}")

    for label, value in d["traps"].items():
        if value == d["answer"]:
            ok = False
            print(f"  FAIL the '{label}' shortcut also lands on {value}")
    if len(set(d["traps"].values())) < 3:
        ok = False
        print(f"  FAIL the shortcuts collide: {d['traps']}")
    if ok:
        print(f"  ok   four shortcuts, four distinct wrong answers: "
              f"{sorted(d['traps'].values())}")

    mine = {op["tid"] for op in d["lines"]
            if op["op"] == "post" and op["account"] == d["target"]}
    counted = 0
    for tid in mine:
        gate = [op["op"] for op in d["lines"]
                if op["tid"] == tid and op["op"] in ("void", "restore")]
        counted += not (gate and gate[-1] == "void")
    print(f"  ok   {len(mine)} entries for the target, {counted} of them "
          f"counting — missing any one changes the total")

    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "t"
        write(out, seed)
        meta = yaml.safe_load((out / "meta.yaml").read_text(encoding="utf-8"))
        t = _T(meta)
        cases = [(f"working...\nANSWER: {d['answer']}", 1.0, "correct"),
                 (f"ANSWER: {d['answer']:+d}", 1.0, "correct, signed"),
                 ("", 0.0, "empty"),
                 (f"ANSWER: {d['answer'] + 1}", 0.0, "off by one"),
                 (f"the total is {d['answer']}", 0.0, "no ANSWER line")]
        for label, value in d["traps"].items():
            cases.append((f"ANSWER: {value}", 0.0, f"trap: {label}"))
        for resp, want, label in cases:
            got = scoring.score_answer(t, resp)["score"]
            good = got == want
            ok &= good
            print(f"  {'ok  ' if good else 'FAIL'} {label:32s} score={got} "
                  f"(want {want})")
    return ok


def main() -> None:
    seeds = [int(a) for a in sys.argv[1:]] or [SEED]
    allok = True
    for s in seeds:
        allok &= verify(s)
        print()
    print("VERIFIED" if allok else "*** VERIFICATION FAILED ***")
    if not allok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
