# Write test file with trailing newline
with open("test_trail_nl.txt", "w") as f:
    f.write("line one\nline two\n")

# Write test file without trailing newline
with open("test_no_trail_nl.txt", "w") as f:
    f.write("line one\nline two")