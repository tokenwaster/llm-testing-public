import subprocess

def run_test(filename, content):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    result = subprocess.run(['python', 'wordstats.py', filename], capture_output=True, text=True)
    return result.stdout

# Case 1: Standard text
# lines: 3
# words: "hello", "world", "hello", "foo" -> 4
# top: hello 2
test1 = "Hello World!\nhello foo\nbar" # wait, bar is there too.
# Let's be precise:
# Hello (1), World (2), hello (3), foo (4), bar (5)
# words: hello (2), world (1), foo (1), bar (1)
# top: hello 2

# Case 2: Tie break
# "apple apple banana banana" -> apple 2, banana 2. Top should be apple.
test2 = "apple banana\nbanana apple"

# Case 3: No words
test3 = "123 456\n!!! ???\n   "

# Case 4: Empty file
test4 = ""

# Case 5: Trailing newline
# lines should be 1, not 2.
test5 = "hello world\n"

print("Running tests...")

print("Test 1:")
print(run_test('t1.txt', 'Hello World!\nhello foo\nbar'))

print("\nTest 2 (Tie break):")
print(run_test('t2.txt', 'apple banana\nbanana apple'))

print("\nTest 3 (No words):")
print(run_test('t3.txt', '123 456\n!!! ???\n   '))

print("\nTest 4 (Empty file):")
print(run_test('t4.txt', ''))

print("\nTest 5 (Trailing newline):")
print(run_test('t5.txt', 'hello world\n'))
