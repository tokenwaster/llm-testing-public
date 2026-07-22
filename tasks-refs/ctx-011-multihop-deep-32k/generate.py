"""Generator + reference for ctx-011-multihop-deep-32k (v0.6 long-context overhaul).

Answering needs a 4-hop chain (project -> squad -> cell -> hub -> zone) whose
links are scattered at random through ~1,300 shuffled lines, most of them decoy
links for other entities. A big window doesn't help: you must actually follow
the chain, and every wrong turn lands on a plausible decoy. Answer computed by
construction.
"""

import random
from pathlib import Path

SEED = 20260716
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "tasks-staging" / "long-context" / "ctx-011-multihop-deep-32k"

FILLER = [
    "monthly capacity review filed; no reallocation required.",
    "on-call rotation published for the coming cycle.",
    "asset inventory reconciled against the central manifest.",
    "training compliance confirmed for all listed staff.",
    "budget variance report acknowledged by finance.",
]


def ids(prefix, n, rng):
    out = set()
    while len(out) < n:
        out.add(f"{prefix}-{rng.randint(100, 999)}")
    return sorted(out)


def build():
    rng = random.Random(SEED)
    projects = ids("P", 40, rng)
    squads = ids("SQ", 30, rng)
    cells = ids("CE", 22, rng)
    hubs = ids("HB", 14, rng)
    zones = ids("ZN", 8, rng)

    p2s = {p: rng.choice(squads) for p in projects}
    s2c = {s: rng.choice(cells) for s in squads}
    c2h = {c: rng.choice(hubs) for c in cells}
    h2z = {h: rng.choice(zones) for h in hubs}

    target = rng.choice(projects)
    answer = h2z[c2h[s2c[p2s[target]]]]

    lines = []
    for p, s in p2s.items():
        lines.append(f"Project {p} is run by squad {s}.")
    for s, c in s2c.items():
        lines.append(f"Squad {s} operates out of cell {c}.")
    for c, h in c2h.items():
        lines.append(f"Cell {c} is administered by hub {h}.")
    for h, z in h2z.items():
        lines.append(f"Hub {h} belongs to zone {z}.")
    while len(lines) < 1300:
        who = rng.choice(projects + squads + cells + hubs)
        lines.append(f"{who}: {rng.choice(FILLER)}")
    rng.shuffle(lines)
    body = "\n".join(lines)

    prompt = (
        "You are given a long, unordered directory of organisational links. "
        "Projects belong to squads, squads to cells, cells to hubs, and hubs to "
        "zones. Each entity maps to exactly one parent.\n\n"
        f"Trace the chain and report which ZONE **{target}** ultimately belongs "
        f"to: follow {target} -> its squad -> that squad's cell -> that cell's "
        f"hub -> that hub's zone. Only the exact chain counts; sibling links for "
        f"other entities are decoys.\n\n"
        "Reply with the zone id exactly as written (e.g. `ZN-123`).\n\n"
        "--- BEGIN DIRECTORY ---\n" + body + "\n--- END DIRECTORY ---\n"
    )
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "prompt.md").write_text(prompt, encoding="utf-8")
    (OUT / "meta.yaml").write_text(
        "id: ctx-011-multihop-deep-32k\n"
        "category: long-context\n"
        "tier: 1\n"
        "title: 4-hop chain trace under distractors @ 32k\n"
        "timeout_s: 600\n"
        "max_retries: 1\n"
        "scoring:\n"
        "  type: answer\n"
        f"  answer: \"{answer}\"\n"
        "  match: exact\n", encoding="utf-8")
    return target, answer, len(lines), prompt


if __name__ == "__main__":
    target, answer, n, prompt = build()
    print(f"wrote {OUT}")
    print(f"target={target}  answer(zone)={answer}  lines={n}  ~tokens={len(prompt)//4:,}")
