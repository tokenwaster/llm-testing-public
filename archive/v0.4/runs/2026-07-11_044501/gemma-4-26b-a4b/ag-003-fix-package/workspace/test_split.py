text = "  multiple   spaces\t\nand\ttabs  "
print(f"'{text.split()}'")
print(f"Lengths: {[len(w) for w in text.split()]}")
print(f"Sum: {sum(len(w) for w in text.split())}")
print(f"Count: {len(text.split())}")
print(f"Avg: {sum(len(w) for w in text.split()) / len(text.split())}")
