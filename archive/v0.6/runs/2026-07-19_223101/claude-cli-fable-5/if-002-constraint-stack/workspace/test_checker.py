"""if-002 (frontier): five interlocking constraints — acrostic FROND, strictly
increasing length, exactly one palindrome, and a total-letter count divisible by
5. Each is independent, and satisfying all at once (while the length ladder
limits word choice) is what makes strong models slip.
"""
import pathlib

_TXT = pathlib.Path("response.txt")
TEXT = _TXT.read_text(encoding="utf-8") if _TXT.exists() else ""
LINES = [ln.strip() for ln in TEXT.strip().splitlines()]
WORDS = LINES[:5]


def test_exactly_five_lowercase_words():
    assert len(LINES) == 5, f"expected 5 lines, got {len(LINES)}"
    assert all(w.isalpha() and w.islower() for w in WORDS), \
        f"each line must be one lowercase a-z word: {WORDS}"


def test_acrostic_spells_frond():
    assert len(WORDS) == 5 and all(WORDS), "need five words"
    assert "".join(w[0] for w in WORDS) == "frond", \
        f"first letters spell {''.join(w[0] for w in WORDS if w)!r}, need 'frond'"


def test_strictly_increasing_length():
    lens = [len(w) for w in WORDS]
    assert len(lens) == 5, "need five words"
    assert all(a < b for a, b in zip(lens, lens[1:])), \
        f"lengths not strictly increasing: {lens}"


def test_exactly_one_palindrome():
    pals = [w for w in WORDS if len(w) > 1 and w == w[::-1]]
    assert len(pals) == 1, f"need exactly one palindrome, found {pals}"


def test_total_letters_multiple_of_five():
    total = sum(len(w) for w in WORDS)
    assert len(WORDS) == 5, "need five words"
    assert total % 5 == 0, f"total letters {total} is not a multiple of 5"
