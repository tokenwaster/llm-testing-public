from textstats import summarize


def test_basic():
    assert summarize("the cat sat") == {"words": 3, "unique": 3, "avg_len": 3.0}


def test_any_whitespace():
    r = summarize("one\ttwo\nthree   four")
    assert r["words"] == 4
    assert r["unique"] == 4


def test_case_insensitive_unique():
    r = summarize("Dog dog DOG")
    assert r["words"] == 3
    assert r["unique"] == 1


def test_punctuation_stripped():
    r = summarize('"Dog." said the dog!')
    assert r["words"] == 4
    assert r["unique"] == 3          # dog, said, the
    assert r["avg_len"] == 3.25      # dog(3) + said(4) + the(3) + dog(3) = 13/4


def test_pure_punctuation_not_a_word():
    r = summarize("hello ... world !!")
    assert r["words"] == 2
    assert r["unique"] == 2


def test_empty_input():
    assert summarize("") == {"words": 0, "unique": 0, "avg_len": 0.0}
    assert summarize("  \n\t ") == {"words": 0, "unique": 0, "avg_len": 0.0}


def test_avg_len_rounding():
    # to(2) + be(2) + or(2) + not(3) = 9/4 = 2.25
    assert summarize("to be or not")["avg_len"] == 2.25
