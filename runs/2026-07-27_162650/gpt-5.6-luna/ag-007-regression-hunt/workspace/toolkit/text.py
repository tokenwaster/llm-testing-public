import re


def title_case(s: str) -> str:
    # str.title() capitalizes the first letter after an apostrophe too
    # (e.g. ``dog'S``), which is not the usual word-style convention.
    titled = s.title()
    return re.sub(
        r"(?<=[A-Za-z])'([A-Za-z]+)",
        lambda match: "'" + match.group(1).lower(),
        titled,
    )


def snake_case(s: str) -> str:
    out = []
    for i, ch in enumerate(s):
        if ch.isupper() and i > 0 and (s[i - 1].islower()
                                       or (i + 1 < len(s)
                                           and s[i + 1].islower())):
            out.append("_")
        out.append(ch.lower())
    return "".join(out).replace(" ", "_").replace("-", "_")


def truncate(s: str, limit: int) -> str:
    if len(s) <= limit:
        return s
    return s[: max(limit - 1, 0)] + "…"
