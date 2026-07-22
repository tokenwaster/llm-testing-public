import importlib

def get_module_attr(module_name, attr):
    try:
        module = importlib.import_module(f"pipeline.{module_name}")
        return getattr(module, attr)
    except (ImportError, AttributeError):
        return None

def main():
    # Start with the module name from entry.py
    # I already know START = "mod_27" from reading it, but let's be robust.
    try:
        import pipeline.entry as entry
        current_module_name = entry.START
    except Exception as e:
        print(f"Error loading entry module: {e}")
        return

    count = 1
    print(f"Module 1: {current_module_name}")

    while count < 7:
        next_module_name = get_module_attr(current_module_name, "NEXT")
        if next_module_name is None:
            print("Reached the end of the chain before 7 modules.")
            break
        
        current_module_name = next_module_name
        count += 1
        print(f"Module {count}: {current_module_name}")

    if count == 7:
        token = get_module_attr(current_module_name, "SECRET_TOKEN")
        print(f"Found token: {token}")
        with open("answer.txt", "w") as f:
            f.write(str(token))
    else:
        print("Failed to reach 7 modules.")

if __name__ == "__main__":
    main()
