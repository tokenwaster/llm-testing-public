import re
from datetime import date


_MONTHS_FULL = {
    name.lower(): month
    for month, name in enumerate(
        (
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December",
        ),
        start=1,
    )
}

_MONTHS_ABBR = {
    name.lower(): month
    for month, name in enumerate(
        (
            "Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
        ),
        start=1,
    )
}


def normalize_date(text: str) -> str | None:
    if not isinstance(text, str):
        return None

    value = text.strip()

    patterns = (
        (r"(\d{4})-(\d{2})-(\d{2})", lambda m: (int(m.group(1)), int(m.group(2)), int(m.group(3)))),
        (r"(\d{1,2})/(\d{1,2})/(\d{4})", lambda m: (int(m.group(3)), int(m.group(2)), int(m.group(1)))),
        (
            r"([A-Za-z]+)\s+(\d{1,2}),\s+(\d{4})",
            lambda m: (int(m.group(3)), _MONTHS_FULL.get(m.group(1).lower()), int(m.group(2))),
        ),
        (
            r"(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})",
            lambda m: (int(m.group(3)), _MONTHS_ABBR.get(m.group(2).lower()), int(m.group(1))),
        ),
    )

    for pattern, parser in patterns:
        match = re.fullmatch(pattern, value)
        if match:
            try:
                year, month, day = parser(match)
                if month is None:
                    return None
                return date(year, month, day).isoformat()
            except ValueError:
                return None

    return None
