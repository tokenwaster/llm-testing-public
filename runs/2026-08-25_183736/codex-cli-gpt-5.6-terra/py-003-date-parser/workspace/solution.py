import re
from datetime import date


def normalize_date(text: str) -> str | None:
    value = text.strip()

    try:
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            year, month, day = map(int, value.split("-"))
            return date(year, month, day).isoformat()

        match = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", value)
        if match:
            day, month, year = map(int, match.groups())
            return date(year, month, day).isoformat()

        match = re.fullmatch(
            r"(January|February|March|April|May|June|July|August|September|October|November|December)"
            r"\s+(\d{1,2}),\s+(\d{4})",
            value,
            re.IGNORECASE,
        )
        if match:
            month_name, day, year = match.groups()
            month = (
                "january february march april may june july august "
                "september october november december"
            ).split().index(month_name.lower()) + 1
            return date(int(year), month, int(day)).isoformat()

        match = re.fullmatch(
            r"(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})",
            value,
            re.IGNORECASE,
        )
        if match:
            day, month_name, year = match.groups()
            month = (
                "jan feb mar apr may jun jul aug sep oct nov dec"
            ).split().index(month_name.lower()) + 1
            return date(int(year), month, int(day)).isoformat()
    except ValueError:
        return None

    return None
