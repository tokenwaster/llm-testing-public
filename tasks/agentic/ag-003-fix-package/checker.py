"""ag-003 checker. Redesigned so a no-op (unedited seed) scores ~0: every test
exercises at least one of the three bugs — tokenize must split on ANY
whitespace, clean must be case-insensitive, and summarize must not divide by
zero on empty input. A correct fix scores 1.0; partial fixes score in between."""
from textstats import summarize


def test_word_count_any_whitespace():
    r = summarize("one\ttwo\nthree   four")
    assert r["words"] == 4
    assert r["unique"] == 4


def test_newlines_and_tabs_are_separators():
    assert summarize("a\nb\tc d")["words"] == 4


def test_case_insensitive_unique():
    assert summarize("Dog dog DOG")["unique"] == 1


def test_case_insensitive_across_whitespace():
    r = summarize("Cat\ncat  CAT\tcat")
    assert r["words"] == 4
    assert r["unique"] == 1


def test_punctuation_stripped_case_insensitive():
    r = summarize('"Dog." said the dog!')
    assert r["words"] == 4
    assert r["unique"] == 3
    assert r["avg_len"] == 3.25


def test_punct_and_whitespace_variety():
    r = summarize('The\tquick! "brown"\nthe QUICK')
    assert r["words"] == 5
    assert r["unique"] == 3


def test_pure_punctuation_not_a_word():
    r = summarize("hello\t...\nworld !!")
    assert r["words"] == 2
    assert r["unique"] == 2


def test_empty_input_no_raise():
    assert summarize("") == {"words": 0, "unique": 0, "avg_len": 0.0}


def test_whitespace_only_no_raise():
    assert summarize("  \n\t ") == {"words": 0, "unique": 0, "avg_len": 0.0}


def test_avg_len_over_mixed_whitespace():
    assert summarize("to\tbe or\nnot")["avg_len"] == 2.25
