"""Generator + reference for rs-011-gear-axle-train (v0.6 reasoning trap).

The trap: a chain of gears, but only some pairs MESH (ratio applies, direction
flips). Others share an AXLE with the previous gear (same rpm, same direction —
NO ratio). The obvious move is to apply a ratio at every step; that is wrong.
Final rpm is computed exactly by construction, so the key can't be wrong. A
model that treats an axle as a mesh (or vice versa) lands far from the answer.
"""

import random
from fractions import Fraction
from pathlib import Path

SEED = 20260716
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "tasks-refs" / "rs-011-gear-axle-train"
STAGE = ROOT / "tasks-staging" / "reasoning" / "rs-011-gear-axle-train"


def build():
    rng = random.Random(SEED)
    n = 9
    driver_rpm = rng.choice([120, 144, 180, 240])
    teeth = [rng.choice([12, 15, 18, 20, 24, 30, 36, 40]) for _ in range(n)]
    links = [None] + [rng.choice(["mesh", "mesh", "axle"]) for _ in range(1, n)]

    rpm = Fraction(driver_rpm)
    for i in range(1, n):
        if links[i] == "mesh":
            rpm *= Fraction(teeth[i - 1], teeth[i])
    answer = round(float(rpm), 2)

    desc = [f"Gear 1 is the driver: it has {teeth[0]} teeth and turns at "
            f"{driver_rpm} rpm."]
    for i in range(1, n):
        if links[i] == "mesh":
            desc.append(f"Gear {i+1} ({teeth[i]} teeth) MESHES with gear {i}.")
        else:
            desc.append(f"Gear {i+1} ({teeth[i]} teeth) is fixed on the SAME "
                        f"SHAFT as gear {i}.")

    prompt = (
        "A gear train has 9 gears in a line. Two gears can be connected two ways:\n"
        "- **Meshing**: their teeth engage. A meshed gear's speed is the other "
        "gear's speed times (other's teeth / this gear's teeth).\n"
        "- **Same shaft**: two gears fixed on one axle turn at the SAME rpm "
        "(a shared shaft is not a mesh — no tooth ratio applies).\n\n"
        + "\n".join(desc) +
        "\n\nWhat is the rpm of **gear 9**? Reply with the number (2 decimals), "
        "e.g. `73.50`.\n"
    )
    STAGE.mkdir(parents=True, exist_ok=True)
    (STAGE / "prompt.md").write_text(prompt, encoding="utf-8")
    (STAGE / "meta.yaml").write_text(
        "id: rs-011-gear-axle-train\n"
        "category: reasoning\n"
        "tier: 1\n"
        "title: Gear train with shared-shaft trap\n"
        "timeout_s: 300\n"
        "max_retries: 1\n"
        "scoring:\n"
        "  type: answer\n"
        f"  answer: \"{answer}\"\n"
        "  match: numeric\n"
        "  tolerance: 0.1\n", encoding="utf-8")
    return answer, links, prompt


if __name__ == "__main__":
    answer, links, prompt = build()
    print(f"wrote {STAGE}")
    print(f"answer(gear9 rpm)={answer}  links={links[1:]}")
