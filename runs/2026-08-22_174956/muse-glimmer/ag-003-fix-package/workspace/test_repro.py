from textstats import summarize

tests = [
    ("", {"words":0,"unique":0,"avg_len":0.0}),
    ("   \n\t  ", {"words":0,"unique":0,"avg_len":0.0}),
    ("Hello", {"words":1,"unique":1,"avg_len":5.0}),
    ("Hello hello", {"words":2,"unique":1,"avg_len":5.0}),
    ("Dog. dog", {"words":2,"unique":1,"avg_len":3.0}),
    ("Hello, world!", {"words":2,"unique":2,"avg_len":5.0}), # Hello, -> Hello (5), world! -> world (5) avg 5
    ("  multiple   spaces\tand\nnewlines ", {"words":4,"unique":4,"avg_len": None}), # just check count
    ("... !!!", {"words":0,"unique":0,"avg_len":0.0}),
    ("'Hello' (world)", {"words":2,"unique":2,"avg_len":5.0}),
]

for text, expected in tests:
    try:
        result = summarize(text)
        print(f"Input: {repr(text)}")
        print(f"  Result: {result}")
        print(f"  Expected: {expected}")
        # check words and unique, avg_len approx
        ok = result["words"] == expected["words"] and result["unique"] == expected["unique"]
        if expected["avg_len"] is not None:
            ok = ok and abs(result["avg_len"] - expected["avg_len"]) < 0.01
        print("  PASS" if ok else "  FAIL")
    except Exception as e:
        print(f"Input: {repr(text)} -> Exception: {e} FAIL")
    print()
