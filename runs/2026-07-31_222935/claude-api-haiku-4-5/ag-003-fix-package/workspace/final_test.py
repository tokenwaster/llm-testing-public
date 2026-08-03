from textstats import summarize

test_cases = [
    # (input, expected_output)
    ("Hello world", {"words": 2, "unique": 2, "avg_len": 5.0}),
    ("Dog dog DOG", {"words": 3, "unique": 1, "avg_len": 3.0}),
    ("Dog. dog", {"words": 2, "unique": 1, "avg_len": 3.0}),
    ("Hello\tworld\ntest", {"words": 3, "unique": 3, "avg_len": 4.67}),
    ("Hello  world   test", {"words": 3, "unique": 3, "avg_len": 4.67}),
    ("Hello ... world", {"words": 2, "unique": 2, "avg_len": 5.0}),
    ("", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("   \t\n  ", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("...,,,", {"words": 0, "unique": 0, "avg_len": 0.0}),
    ("'Hello!' (world)", {"words": 2, "unique": 2, "avg_len": 5.0}),
    ("\"Test\", test.", {"words": 2, "unique": 1, "avg_len": 4.0}),
    ("Hi world", {"words": 2, "unique": 2, "avg_len": 3.5}),
    ("a b c d e", {"words": 5, "unique": 5, "avg_len": 1.0}),
]

print("Running final comprehensive tests:\n")
all_passed = True
for i, (input_text, expected) in enumerate(test_cases, 1):
    result = summarize(input_text)
    passed = result == expected
    all_passed = all_passed and passed
    status = "PASS" if passed else "FAIL"
    print("Test {}: {}".format(i, status))
    if not passed:
        print("  Input: {}".format(repr(input_text)))
        print("  Expected: {}".format(expected))
        print("  Got:      {}".format(result))
    print()

if all_passed:
    print("All tests passed!")
else:
    print("Some tests failed!")
