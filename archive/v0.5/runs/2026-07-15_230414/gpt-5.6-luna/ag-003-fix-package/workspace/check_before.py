from textstats import summarize

for text in ["Dog. dog", "a\tb\n c", "!!! ...", ""]:
    try:
        print(repr(text), summarize(text))
    except Exception as e:
        print(repr(text), type(e).__name__, str(e))
