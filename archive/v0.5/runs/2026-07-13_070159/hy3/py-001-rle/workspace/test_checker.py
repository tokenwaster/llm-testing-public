from solution import encode, decode


def test_encode_basic():
    assert encode("aaabcc") == "3a1b2c"


def test_encode_single_chars():
    assert encode("abc") == "1a1b1c"


def test_encode_empty():
    assert encode("") == ""


def test_encode_case_sensitive():
    assert encode("aAA") == "1a2A"


def test_decode_basic():
    assert decode("3a1b2c") == "aaabcc"


def test_decode_multidigit():
    assert decode("12a1b") == "a" * 12 + "b"


def test_decode_empty():
    assert decode("") == ""


def test_roundtrip():
    for s in ["a", "zzzzzzzzzzzzzz", "abcABC", "aabbaabb", "Q" * 100 + "w"]:
        assert decode(encode(s)) == s
