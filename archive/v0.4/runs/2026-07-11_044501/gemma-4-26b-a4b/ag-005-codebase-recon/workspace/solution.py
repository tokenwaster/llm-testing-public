import importlib
import os

def solve():
    current_module_name = None
    try:
        import pipeline.entry as entry
        current_module_name = entry.START
        print(f"Starting module: {current_module_name}")
    except Exception as e:
        print(f"Error loading entry: {e}")
        return

    count = 1
    while count < 7:
        module_path = f"pipeline.{current_module_name}"
        try:
            module = importlib.import_module(module_path)
            next_module_name = getattr(module, "NEXT", None)
            if next_module_name is None:
                print(f"Reached end of chain at {current_module_name}")
                break
            current_module_name = next_module_name
            count += 1
            print(f"Step {count}: moved to {current_module_name}")
        except Exception as e:
            print(f"Error loading module {module_path}: {e}")
            break

    # Now we are at the 7th module (or end of chain)
    final_module_path = f"pipeline.{current_module_name}"
    print(f"Final module to check: {final_module_path} (count={count})")
    try:
        final_module = importlib.import_module(final_module_path)
        token = getattr(final_module, "SECRET_TOKEN")
        print(f"Found token: {token}")
        with open("answer.txt", "w") as f:
            f.write(str(token))
    except Exception as e:
        print(f"Error getting token from {final_module_path}: {e}")

if __name__ == "__main__":
    solve()
