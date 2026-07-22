"""The public/private boundary: the open-source instrument must never import the
operator layer. If it does, the public repo won't run (the private modules aren't
shipped) and, worse, a private dependency could drag the moat into the open.
See docs/PUBLIC-RELEASE.md. This test ships publicly and stays true there too.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PUBLIC = {"config", "util", "registry", "tasks", "adapters", "scoring", "runner",
          "telemetry", "tools", "lmstudio", "gguf", "report", "fit", "archive",
          "assess", "rescore", "discover", "interfaces", "viewer"}
PRIVATE = {"watch", "jobs", "review", "scout", "rename"}


def test_public_modules_never_import_private_ones():
    offenders = []
    for mod in PUBLIC:
        f = ROOT / "harness" / f"{mod}.py"
        if not f.is_file():
            continue
        src = f.read_text(encoding="utf-8")
        imported = set(re.findall(r"from \.(\w+) import", src))
        imported |= {n.strip() for m in re.findall(r"from \. import ([\w, ]+)", src)
                     for n in m.split(",")}
        for p in imported & PRIVATE:
            offenders.append(f"{mod} imports {p}")
        if re.search(r"(from studio|import studio)\b", src):
            offenders.append(f"{mod} imports studio")
    assert not offenders, "public instrument reaches into the operator layer: " \
        + "; ".join(offenders)
