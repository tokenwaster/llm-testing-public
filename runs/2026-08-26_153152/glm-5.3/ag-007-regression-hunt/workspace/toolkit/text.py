_APOSTROPHES = "'\u2019"


def title_case(s: str) -> str:
    """Title-case ``s``.

    Unlike :meth:`str.title`, an apostrophe does *not* start a new word,
    so ``"it's"`` becomes ``"It's"`` rather than ``"It'S"``.
    """
    out = []
    at_boundary = True
    for ch in s:
        if ch.isalnum() or ch in _APOSTROPHES:
            out.append(ch.upper() if at_boundary else ch.lower())
            at_boundary = False
        else:
            out.append(ch)
            at_boundary = True
    return "".join(out)


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
