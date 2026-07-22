import json
from pathlib import Path

EXPECTED = [
    {"email": "alice@example.com", "signup": "2024-01-20", "score": 88},
    {"email": "bob@mail.net", "signup": "2024-02-15", "score": 91},
    {"email": "carol@site.org", "signup": "2024-03-02", "score": 77},
    {"email": "frank@shop.co", "signup": "2024-06-11", "score": 64},
    {"email": "gina@lab.ai", "signup": "2024-07-07", "score": 70},
]


def load():
    path = Path(__file__).parent / "output.json"
    assert path.exists(), "output.json was not created"
    return json.loads(path.read_text(encoding="utf-8"))


def test_is_list_of_objects():
    data = load()
    assert isinstance(data, list)
    assert all(isinstance(r, dict) for r in data)


def test_exact_keys():
    for r in load():
        assert sorted(r.keys()) == ["email", "score", "signup"], r


def test_row_count():
    assert len(load()) == len(EXPECTED)


def test_content_and_order():
    assert load() == EXPECTED


def test_score_is_integer():
    for r in load():
        assert isinstance(r["score"], int), r
