from pathlib import Path

EXPECTED = "tok_uf9pa9r3sk"


def test_answer_file_exists():
    assert (Path(__file__).parent / "answer.txt").exists(), "answer.txt missing"


def test_answer_value():
    got = (Path(__file__).parent / "answer.txt").read_text(encoding="utf-8").strip()
    assert got == EXPECTED, f"wrong token: {got!r}"
