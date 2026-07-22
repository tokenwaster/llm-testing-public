"""Walk the configured pipeline chain and write its seventh token."""
import ast
from pathlib import Path

ROOT = Path(__file__).parent


def constants(path: Path) -> dict[str, object]:
    tree = ast.parse(path.read_text())
    return {
        node.targets[0].id: ast.literal_eval(node.value)
        for node in tree.body
        if isinstance(node, ast.Assign)
        and len(node.targets) == 1
        and isinstance(node.targets[0], ast.Name)
        and node.targets[0].id in {"START", "NEXT", "SECRET_TOKEN"}
    }

current = constants(ROOT / "pipeline" / "entry.py")["START"]
visited = []
for _ in range(7):
    values = constants(ROOT / "pipeline" / f"{current}.py")
    visited.append((current, values["SECRET_TOKEN"]))
    current = values["NEXT"]

(ROOT / "answer.txt").write_text(str(visited[-1][1]))
print(" -> ".join(name for name, _ in visited))
print(visited[-1][1])
