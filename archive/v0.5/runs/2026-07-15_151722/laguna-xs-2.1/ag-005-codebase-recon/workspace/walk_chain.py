import importlib

# Start from the START module
current = "mod_27"
visited = 0

while visited < 7:
    module = importlib.import_module(f"pipeline.{current}")
    print(f"Module {visited + 1}: {current}")
    print(f"  SECRET_TOKEN: {module.SECRET_TOKEN}")
    print(f"  NEXT: {module.NEXT}")
    
    if visited == 6:  # 7th module (0-indexed)
        with open("answer.txt", "w") as f:
            f.write(module.SECRET_TOKEN)
        print(f"\nWritten SECRET_TOKEN to answer.txt: {module.SECRET_TOKEN}")
    
    current = module.NEXT
    visited += 1