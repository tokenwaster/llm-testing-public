from textstats import summarize

def test():
    test_cases = [
        ("", {"words": 0, "unique": 0, "avg_len": 0.0}),
        ("   ", {"words": 0, "unique": 0, "avg_len": 0.0}),
        ("Hello world", {"words": 2, "unique": 2, "avg_len": 5.0}),
        ("Dog. dog", {"words": 2, "unique": 1, "avg_len": 3.0}),
        ("... !!! ...", {"words": 0, "unique": 0, "avg_len": 0.0}),
        ("One, two; three!", {"words": 3, "unique": 3, "avg_len": 3.67}), # (3+3+5)/3 = 11/3 = 3.666... -> 3.67
        ("  apple   banana\ncherry\tdate ", {"words": 4, "unique": 4, "avg_len": 5.25}), # (5+6+6+4)/4 = 21/4 = 5.25
    ]

    for i, (input_str, expected) in enumerate(test_cases):
        try:
            result = summarize(input_str)
            if result != expected:
                print(f"Test case {i} failed!")
                print(f"  Input: {repr(input_str)}")
                print(f"  Expected: {expected}")
                print(f"  Actual:   {result}")
                exit(1)
            else:
                print(f"Test case {i} passed!")
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Test case {i} raised an exception: {e}")
            exit(1)

if __name__ == "__main__":
    test()
