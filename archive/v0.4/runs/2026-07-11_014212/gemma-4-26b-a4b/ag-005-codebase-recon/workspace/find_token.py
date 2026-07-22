import importlib
import sys
import os

def main():
    # Add current directory to sys.path so we can import pipeline
    sys.path.append(os.getcwd())

    # Read START from entry.py
    start_module_name = None
    try:
        with open("pipeline/entry.py", "r") as f:
            content = f.read()
            for line in content.splitlines():
                if line.startswith("START ="):
                    start_module_name = line.split("=")[1].strip().strip("'").strip('"')
                    break
    except Exception as e:
        print(f"Error reading entry.py: {e}")
        return

    if not start_module_name:
        print("Could not find START in pipeline/entry.py")
        return

    current_module_name = start_module_name
    visited_count = 0
    last_token = None

    while current_module_name is not None and visited_count < 7:
        visited_count += 1
        print(f"Visiting {visited_count}: {current_module_name}")
        
        try:
            module = importlib.import_module(f"pipeline.{current_module_name}")
            last_token = getattr(module, "SECRET_TOKEN")
            next_module_name = getattr(module, "NEXT", None)
            
            if visited_count == 7:
                print(f"Found 7th module token: {last_token}")
                with open("answer.txt", "w") as f:
                    f.write(str(last_token))
                break
                
            current_module_name = next_module_name
        except Exception as e:
            print(f"Error at {current_module_name}: {e}")
            break

if __name__ == "__main__":
    main()
