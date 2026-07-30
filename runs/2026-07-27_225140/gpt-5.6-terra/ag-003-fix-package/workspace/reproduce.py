from textstats import summarize

for text in ["Dog. dog", "one\ttwo\nthree", "... !!!", ""]:
    try:
        print(repr(text), summarize(text))
    except Exception as exc:
        print(repr(text), type(exc).__name__, str(exc))
