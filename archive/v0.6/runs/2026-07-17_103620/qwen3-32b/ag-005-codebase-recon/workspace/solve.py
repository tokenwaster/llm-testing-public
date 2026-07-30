import importlib
import sys

sys.path.append(".")

# Read pipeline.entry.START
entry = importlib.import_module("pipeline.entry")
current_name = entry.START

# Follow NEXT six times to reach the seventh module
for _ in range(6):
    module = importlib.import_module(f"pipeline.{current_name}")
    current_name = module.NEXT

# Now get the SECRET_TOKEN of the 7th module
seventh_module = importlib.import_module(f"pipeline.{current_name}")
secret_token = seventh_module.SECRET_TOKEN

# Write to answer.txt
with open("answer.txt", "w") as f:
    f.write(secret_token)