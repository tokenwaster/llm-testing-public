"""A small RFC-4180-style CSV parser implemented from scratch."""

from __future__ import annotations


def parse_csv(text: str) -> list[list[str]]:
    """Parse CSV text into a list of records, each a list of string fields.

    Rules implemented:
      - Fields are separated by commas; records by ``\\n`` or ``\\r\\n``.
      - A field starting with a double quote may contain commas, newlines,
        and escaped quotes (``""`` decodes to a single ``"``).
      - Quotes are only special at the start of a field; otherwise they are
        literal characters.
      - A trailing newline does not produce an extra record, but an empty
        line is a record with one empty field.
      - ``parse_csv("")`` returns ``[]``.
      - Unterminated quoted fields and stray characters after a closing
        quote raise ``ValueError``.
    """
    records: list[list[str]] = []
    row: list[str] = []
    field: list[str] = []

    # Parser states.
    START = 0        # At the beginning of a field.
    UNQUOTED = 1     # Inside an unquoted field.
    QUOTED = 2       # Inside a quoted field.
    AFTER_QUOTE = 3  # Just consumed the closing quote of a quoted field.
    state = START

    def flush_field() -> None:
        nonlocal field
        row.append("".join(field))
        field = []

    def flush_record() -> None:
        nonlocal row
        flush_field()
        records.append(row)
        row = []

    i = 0
    n = len(text)

    while i < n:
        c = text[i]

        if state == START:
            if c == '"':
                state = QUOTED
                i += 1
            elif c == ',':
                flush_field()
                i += 1
            elif c == '\n':
                flush_record()
                i += 1
            elif c == '\r':
                # Treat "\r\n" (and a lone "\r") as a record separator.
                i += 2 if (i + 1 < n and text[i + 1] == '\n') else 1
                flush_record()
            else:
                field.append(c)
                state = UNQUOTED
                i += 1

        elif state == UNQUOTED:
            if c == ',':
                flush_field()
                state = START
                i += 1
            elif c == '\n':
                flush_record()
                state = START
                i += 1
            elif c == '\r':
                i += 2 if (i + 1 < n and text[i + 1] == '\n') else 1
                flush_record()
                state = START
            else:
                # Quotes here have no special meaning.
                field.append(c)
                i += 1

        elif state == QUOTED:
            if c == '"':
                if i + 1 < n and text[i + 1] == '"':
                    # Doubled quote -> literal quote character.
                    field.append('"')
                    i += 2
                else:
                    state = AFTER_QUOTE
                    i += 1
            else:
                # Everything else (commas, newlines, ...) is literal data.
                field.append(c)
                i += 1

        else:  # AFTER_QUOTE
            if c == ',':
                flush_field()
                state = START
                i += 1
            elif c == '\n':
                flush_record()
                state = START
                i += 1
            elif c == '\r':
                i += 2 if (i + 1 < n and text[i + 1] == '\n') else 1
                flush_record()
                state = START
            else:
                raise ValueError(
                    f"Malformed CSV: unexpected character {c!r} "
                    "after closing quote"
                )

    if state == QUOTED:
        raise ValueError("Malformed CSV: unterminated quoted field")

    if state in (UNQUOTED, AFTER_QUOTE):
        # Input ended in the middle of a field/record: flush it.
        flush_record()
    elif state == START and row:
        # Input ended right after a comma: a final empty field is pending.
        flush_record()
    # Otherwise the input was empty or ended with a newline: nothing pending.

    return records
