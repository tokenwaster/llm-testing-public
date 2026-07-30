from solution import normalize_date


def test_iso_passthrough():
    assert normalize_date("2024-03-05") == "2024-03-05"


def test_slashes_dmy():
    assert normalize_date("05/03/2024") == "2024-03-05"


def test_slashes_unpadded():
    assert normalize_date("5/3/2024") == "2024-03-05"


def test_full_month_name():
    assert normalize_date("March 5, 2024") == "2024-03-05"


def test_full_month_case_insensitive():
    assert normalize_date("mArCh 5, 2024") == "2024-03-05"


def test_abbreviated_month():
    assert normalize_date("5 Mar 2024") == "2024-03-05"
    assert normalize_date("25 dec 2023") == "2023-12-25"


def test_whitespace_tolerated():
    assert normalize_date("  2024-03-05  ") == "2024-03-05"


def test_invalid_calendar_date():
    assert normalize_date("31/02/2024") is None


def test_garbage_returns_none():
    assert normalize_date("not a date") is None
    assert normalize_date("2024/03/05") is None
    assert normalize_date("") is None
