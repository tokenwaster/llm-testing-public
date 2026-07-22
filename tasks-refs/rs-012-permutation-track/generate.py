"""Generator + reference for rs-012-permutation-track (v0.6 reasoning trap).

A row of numbered cups, a sequence of swap/rotate operations, then: where did
the ball that STARTED under cup K end up? Pure state-tracking — models that skim
the ops or track the wrong direction lose the ball. Answer computed by applying
the ops, so the key is exact. Not memorizable: novel op sequence each build.
"""

import random
from pathlib import Path

SEED = 20260716
ROOT = Path(__file__).resolve().parents[2]
STAGE = ROOT / "tasks-staging" / "reasoning" / "rs-012-permutation-track"


def build():
    rng = random.Random(SEED)
    n = 7
    pos = list(range(1, n + 1))
    ops_text = []
    for _ in range(12):
        kind = rng.choice(["swap", "swap", "rotate"])
        if kind == "swap":
            a, b = rng.sample(range(1, n + 1), 2)
            pos[a - 1], pos[b - 1] = pos[b - 1], pos[a - 1]
            ops_text.append(f"Swap the contents of cup {a} and cup {b}.")
        else:
            d = rng.choice(["right", "left"])
            if d == "right":
                pos = [pos[-1]] + pos[:-1]
                ops_text.append("Rotate every cup's contents one place to the "
                                "RIGHT (the last cup's ball wraps to the first).")
            else:
                pos = pos[1:] + [pos[0]]
                ops_text.append("Rotate every cup's contents one place to the "
                                "LEFT (the first cup's ball wraps to the last).")
    moved = [c for c in range(1, n + 1) if pos.index(c) + 1 != c]
    start_cup = rng.choice(moved) if moved else rng.randint(1, n)
    answer = pos.index(start_cup) + 1

    prompt = (
        f"There are {n} cups in a row, numbered 1..{n}. Cup i starts with a ball "
        f"labelled i (so cup 1 has ball 1, etc.). Apply these operations in order:\n\n"
        + "\n".join(f"{i+1}. {t}" for i, t in enumerate(ops_text)) +
        f"\n\nAfter all operations, which CUP holds the ball that started under "
        f"cup **{start_cup}** (i.e. ball {start_cup})? Reply with the cup number, "
        f"e.g. `3`.\n"
    )
    STAGE.mkdir(parents=True, exist_ok=True)
    (STAGE / "prompt.md").write_text(prompt, encoding="utf-8")
    (STAGE / "meta.yaml").write_text(
        "id: rs-012-permutation-track\n"
        "category: reasoning\n"
        "tier: 1\n"
        "title: Track one ball through swaps and rotations\n"
        "timeout_s: 300\n"
        "max_retries: 1\n"
        "scoring:\n"
        "  type: answer\n"
        f"  answer: \"{answer}\"\n"
        "  match: numeric\n"
        "  tolerance: 0\n", encoding="utf-8")
    return start_cup, answer, prompt


if __name__ == "__main__":
    start, answer, prompt = build()
    print(f"wrote {STAGE}")
    print(f"start_cup={start}  answer(final cup)={answer}")
