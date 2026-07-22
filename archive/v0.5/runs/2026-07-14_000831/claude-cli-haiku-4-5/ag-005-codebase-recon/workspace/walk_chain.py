#!/usr/bin/env python3
import sys
from pathlib import Path

workspace = Path(r"E:\Programming\LLM Testing\runs\2026-07-14_000831\claude-cli-haiku\ag-005-codebase-recon\workspace")
sys.path.insert(0, str(workspace))

from pipeline.entry import START

current_module_name = START
chain = []

for hop in range(7):
    # Import the module dynamically
    module = __import__(f"pipeline.{current_module_name}", fromlist=["NEXT", "SECRET_TOKEN"])

    chain.append({
        "hop": hop + 1,
        "module": current_module_name,
        "secret_token": module.SECRET_TOKEN,
        "next": module.NEXT
    })

    print(f"Hop {hop + 1}: {current_module_name} -> TOKEN: {module.SECRET_TOKEN} -> NEXT: {module.NEXT}")

    if module.NEXT is None:
        print(f"WARNING: Reached end of chain at hop {hop + 1} (expected 7)")
        break

    current_module_name = module.NEXT

print("\n" + "="*50)
print(f"7th module: {chain[6]['module']}")
print(f"7th module SECRET_TOKEN: {chain[6]['secret_token']}")
