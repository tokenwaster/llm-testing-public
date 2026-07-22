"""Generator + reference for ctx-010-decoy-recall-32k (v0.6 long-context overhaul).

Why this task: v0.5 showed plain needle-recall is free for modern windows
(ctx-001/002 100% aced). This makes retrieval require PRECISION rather than
window size:

  - the needle matches on TWO constraints (person AND system), not one, and the
    doc is flooded with near-duplicate decoys that satisfy exactly one of them;
  - the target has SEVERAL entries over time (rotation) — only the LATEST key is
    current; the earlier ones are planted as tempting wrong answers.

A big context window doesn't help; carelessly grabbing the first "MAPLE" line,
or the right person's key for the wrong system, or a rotated-out key, all fail.

The answer is correct BY CONSTRUCTION (this script computes it), which is the
task's reference verification — plus we assert a wrong/empty answer scores 0.

Run:  python tasks-refs/ctx-010-decoy-recall-32k/generate.py   (writes the staged task)
"""

import random
from pathlib import Path

SEED = 20260716
N_LINES = 1300
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "tasks-staging" / "long-context" / "ctx-010-decoy-recall-32k"

PEOPLE = ["Nadia Okonkwo", "Priya Ramachandran", "Tomas Novak", "Wei Chen",
          "Layla Haddad", "Ingrid Solberg", "Marcus Bello", "Sofia Vargas",
          "Kenji Watanabe", "Amara Diallo", "Rafael Costa", "Yuki Tanaka",
          "Elena Petrova", "Omar Farouk", "Grace Mbeki", "Hana Kim"]
SYSTEMS = ["vault-atlas", "vault-borealis", "vault-cinder", "vault-drift",
           "vault-ember", "vault-frost", "vault-gale", "vault-harbor",
           "relay-north", "relay-south", "ledger-prime", "ledger-shadow"]
KEYWORDS = ["MAPLE", "QUARTZ", "CINDER", "HELIX", "OTTER", "BASALT", "NIMBUS",
            "SORREL", "VESPER", "GRANITE", "COBALT", "TERRA", "AMBER", "FLINT",
            "ONYX", "WILLOW", "PELICAN", "GARNET", "SABLE", "JUNIPER"]
FILLER = [
    "routine key-rotation audit completed; no anomalies noted.",
    "access review signed off by the on-call security lead.",
    "badge reader firmware verified against the golden image.",
    "quarterly compliance sweep logged for the records retention system.",
    "night-shift handover notes archived without incident.",
]


def keycode(rng):
    return f"{rng.choice(KEYWORDS)}-{rng.randint(1000, 9999)}"


def build():
    rng = random.Random(SEED)
    target_person = "Priya Ramachandran"
    target_system = "vault-cinder"

    lines = []
    rot_days = sorted(rng.sample(range(5, 360), 4))
    rot_keys = []
    for d in rot_days:
        k = keycode(rng)
        rot_keys.append((d, k))
        lines.append((d, f"[day {d:03d}] key {k} issued to {target_person} "
                         f"for {target_system}; supersedes any prior key."))
    answer_day, answer_key = rot_keys[-1]

    for _ in range(14):
        d = rng.randint(5, 360)
        other_sys = rng.choice([s for s in SYSTEMS if s != target_system])
        lines.append((d, f"[day {d:03d}] key {keycode(rng)} issued to "
                         f"{target_person} for {other_sys}; supersedes any prior key."))
    for _ in range(14):
        d = rng.randint(5, 360)
        other_person = rng.choice([p for p in PEOPLE if p != target_person])
        lines.append((d, f"[day {d:03d}] key {keycode(rng)} issued to "
                         f"{other_person} for {target_system}; supersedes any prior key."))

    while len(lines) < N_LINES - len(FILLER) * 6:
        d = rng.randint(1, 365)
        p = rng.choice([x for x in PEOPLE if x != target_person])
        s = rng.choice([x for x in SYSTEMS if x != target_system])
        lines.append((d, f"[day {d:03d}] key {keycode(rng)} issued to {p} for {s}; "
                         f"supersedes any prior key."))
    for _ in range(len(FILLER) * 6):
        d = rng.randint(1, 365)
        lines.append((d, f"[day {d:03d}] {rng.choice(FILLER)}"))

    def carries(text, code):
        return f"key {code} " in text
    fixed = []
    for d, t in lines:
        if carries(t, answer_key) and not (d == answer_day
                                           and target_person in t
                                           and target_system in t):
            t = t.replace(answer_key, keycode(rng), 1)
        fixed.append((d, t))
    lines = fixed
    assert sum(carries(t, answer_key) for _, t in lines) == 1, "answer not unique"

    rng.shuffle(lines)
    body = "\n".join(t for _, t in lines)

    prompt = (
        "You are given a long, unordered key-issuance log for a facility. Each "
        "issuance line names the KEY, the PERSON it was issued to, and the SYSTEM "
        "it is for. Keys are rotated: when a new key is issued to a person for a "
        "system, it supersedes that person's prior key for that same system.\n\n"
        f"Report the CURRENT key issued to **{target_person}** for "
        f"**{target_system}** — i.e. the most recent (highest day number) "
        f"issuance line matching BOTH that person AND that system. Watch for "
        f"decoys: lines with the right person but a different system, or the "
        f"right system but a different person, do not count.\n\n"
        "Reply with the key exactly as written (e.g. `ONYX-1234`).\n\n"
        "--- BEGIN LOG ---\n" + body + "\n--- END LOG ---\n"
    )
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "prompt.md").write_text(prompt, encoding="utf-8")
    meta = (
        "id: ctx-010-decoy-recall-32k\n"
        "category: long-context\n"
        "tier: 1\n"
        "title: Two-constraint recall under decoys @ 32k\n"
        "timeout_s: 600\n"
        "max_retries: 1\n"
        "scoring:\n"
        "  type: answer\n"
        f"  answer: \"{answer_key}\"\n"
        "  match: exact\n"
    )
    (OUT / "meta.yaml").write_text(meta, encoding="utf-8")
    return answer_key, answer_day, len(lines), prompt


if __name__ == "__main__":
    key, day, n, prompt = build()
    words = len(prompt.split())
    print(f"wrote {OUT}")
    print(f"answer (current key) = {key}  (issued on day {day})")
    print(f"log lines = {n}  |  ~words = {words:,}")
