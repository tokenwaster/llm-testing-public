"""Walk the dispatch chain and print the SECRET_TOKEN of the 7th module."""
import ast
from pathlib import Path

PKG = Path(__file__).parent / "pipeline"


def get_constants(module_name: str) -> dict:
    src = (PKG / f"{module_name}.py").read_text()
    tree = ast.parse(src)
    consts = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in ("NEXT", "SECRET_TOKEN"):
                    consts[target.id] = ast.literal_eval(node.value)
    return consts


def main() -> None:
    entry_src = (PKG / "entry.py").read_text()
    tree = ast.parse(entry_src)
    start = None
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "START":
                    start = ast.literal_eval(node.value)
    assert start is not None, "START not found"

    chain = []
    current = start
    while current is not None and len(chain) < 7:
        chain.append(current)
        current = get_constants(current)["NEXT"]

    print("Chain:", " -> ".join(chain))
    assert len(chain) == 7, f"Chain ended early after {len(chain)} modules"

    seventh = chain[6]
    token = get_constants(seventh)["SECRET_TOKEN"]
    print(f"7th module: {seventh}")
    print(f"SECRET_TOKEN: {token}")

    Path("answer.txt").write_text(token)
    print("answer.txt written")


if __name__ == "__main__":
    main()
