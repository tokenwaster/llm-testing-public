from textstats import summarize

def test():
    # Test 1: Whitespace handling (tabs, newlines, multiple spaces)
    t1 = "Hello   world\tthis\nis a test"
    res1 = summarize(t1)
    print(f"Test 1: {res1}")
    assert res1["words"] == 6

    # Test 2: Case-insensitivity and punctuation
    t2 = "Dog. dog DOG! (dog)"
    res2 = summarize(t2)
    print(f"Test 2: {res2}")
    assert res2["unique"] == 1
    assert res2["words"] == 4

    # Test 3: Only punctuation tokens
    t3 = "Hello ... world !!!"
    res3 = summarize(t3)
    print(f"Test 3: {res3}")
    assert res3["words"] == 2
    assert res3["unique"] == 2

    # Test 4: Empty input or no words
    t4 = "   ... !!!   "
    res4 = summarize(t4)
    print(f"Test 4: {res4}")
    assert res4 == {"words": 0, "unique": 0, "avg_len": 0.0}

    # Test 5: Average length rounding
    t5 = "Hello world" # (5+5)/2 = 5.0
    res5 = summarize(t5)
    print(f"Test 5: {res5}")
    assert res5["avg_len"] == 5.0

    t6 = "A bb ccc" # (1+2+3)/3 = 2.0
    res6 = summarize(t6)
    print(f"Test 6: {res6}")
    assert res6["avg_len"] == 2.0

    t7 = "Apple Banana Cherry" # (5+6+6)/3 = 17/3 = 5.666... -> 5.67
    res7 = summarize(t7)
    print(f"Test 7: {res7}")
    assert res7["avg_len"] == 5.67

if __name__ == "__main__":
    try:
        test()
        print("All tests passed!")
    except AssertionError as e:
        print("Test failed!")
    except Exception as e:
        print(f"An error occurred: {e}")
