from textstats import summarize


def test_summarize_handles_whitespace_and_case_insensitive_words():
    assert summarize("Dog.\tdog\nCAT,  cat") == {
        "words": 4,
        "unique": 2,
        "avg_len": 3.0,
    }


def test_summarize_ignores_punctuation_only_tokens():
    assert summarize("!!! ??? (,) alpha!") == {
        "words": 1,
        "unique": 1,
        "avg_len": 5.0,
    }


def test_summarize_empty_or_wordless_input_returns_zeroes():
    expected = {"words": 0, "unique": 0, "avg_len": 0.0}
    assert summarize("") == expected
    assert summarize(" \t\n!!! ???") == expected


def test_summarize_rounds_cleaned_word_lengths():
    assert summarize("a, bb; Ccc") == {
        "words": 3,
        "unique": 3,
        "avg_len": 2.0,
    }
