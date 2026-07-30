
from textstats import summarize

def test_summarize():
    # Test case 1: Basic functionality
    # "Hello" (5), "world," (5), "hello!" (5)
    # words: ["hello", "world", "hello"], len=3, unique=2, avg_len=5.0
    case1 = {"input": "Hello world, hello!", "expected": {"words": 3, "unique": 2, "avg_len": 5.0}}
    
    # Test case 2: Case-insensitivity and punctuation stripping
    # "Dog." (3), "dog" (3), "DOG!" (3)
    # words: ["dog", "dog", "dog"], len=3, unique=1, avg_len=3.0
    case2 = {"input": "   Dog.  dog  DOG!   ", "expected": {"words": 3, "unique": 1, "avg_len": 3.0}}
    
    # Test case 3: Whitespace handling (tabs, newlines, multiple spaces)
    # "Hello" (5), "world" (5), "this" (4), "is" (2), "a" (1), "test" (4)
    # words: ["hello", "world", "this", "is", "a", "test"], len=6, unique=6, avg_len=21/6 = 3.5
    case3 = {"input": "Hello\tworld\nthis is   a test.", "expected": {"words": 6, "unique": 6, "avg_len": 3.5}}
    
    # Test case 4: Empty input
    case4 = {"input": "", "expected": {"words": 0, "unique": 0, "avg_len": 0.0}}
    
    # Test case 5: Input with only punctuation (should count as 0 words)
    case5 = {"input": "!!! ???", "expected": {"words": 0, "unique": 0, "avg_len": 0.0}}
    
    # Test case 6: Multiple punctuation and words
    # "word." (4), "word" (4), "word!" (4)
    # words: ["word", "word", "word"], len=3, unique=1, avg_len=4.0
    case6 = {"input": "word. word! word", "expected": {"words": 3, "unique": 1, "avg_len": 4.0}}

    cases = [case1, case2, case3, case4, case5, case6]

    for i, case in enumerate(cases):
        try:
            result = summarize(case["input"])
            if result != case["expected"]:
                print(f"Test {i} failed: input='{case['input']}', expected={case['expected']}, got={result}")
            else:
                print(f"Test {i} passed")
        except Exception as e:
            print(f"Test {i} raised exception: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_summarize()
