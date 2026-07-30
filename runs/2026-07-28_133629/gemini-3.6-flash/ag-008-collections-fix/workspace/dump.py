with open("collkit.py", "r") as f:
    text = f.read()
with open("collkit_out.txt", "w") as f:
    f.write(text)

with open("tests/test_collkit.py", "r") as f:
    test_text = f.read()
with open("test_out.txt", "w") as f:
    f.write(test_text)
