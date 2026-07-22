"""A from-scratch RFC-4180-style CSV parser."""


def parse_csv(text: str) -> list[list[str]]:
    """Parse CSV text into a list of records (each a list of field strings).

    - Fields are separated by commas; records by ``\\n`` or ``\\r\\n``.
    - A field starting with a double quote may contain commas, newlines,
      and escaped quotes (``""`` decodes to a single ``"``).
    - Quotes are only special at the start of a field.
    - Malformed input (unterminated quote, or junk after a closing quote)
      raises ``ValueError``.
    """
    records: list[list[str]] = []
    record: list[str] = []
    field: list[str] = []

    # Parser states.
    START = 0        # at the beginning of a field
    UNQUOTED = 1     # inside an unquoted field
    QUOTED = 2       # inside a quoted field
    AFTER_QUOTE = 3  # just consumed the closing quote of a quoted field
    state = START

    # True once any character belonging to the current record (field char,
    # opening quote, or comma) has been consumed. Distinguishes "no record
    # pending" (e.g. right after a trailing newline) from "empty field
    # pending" (e.g. input ending with a comma).
    pending = False

    i = 0
    n = len(text)
    while i < n:
        ch = text[i]

        if state == QUOTED:
            if ch == '"':
                if i + 1 < n and text[i + 1] == '"':
                    field.append('"')  # doubled quote -> one literal quote
                    i += 2
                else:
                    state = AFTER_QUOTE
                    i += 1
            else:
                # Quoted fields may contain commas and newlines verbatim.
                field.append(ch)
                i += 1
            continue

        # A record separator: either "\n" or "\r\n". (A lone "\r" is not
        # a separator and falls through to be treated as ordinary data.)
        if ch == '\n' or (ch == '\r' and i + 1 < n and text[i + 1] == '\n'):
            i += 2 if ch == '\r' else 1
            record.append(''.join(field))
            records.append(record)
            field = []
            record = []
            state = START
            pending = False
            continue

        if state == START:
            if ch == '"':
                state = QUOTED
            elif ch == ',':
                record.append('')  # empty field
            else:
                field.append(ch)
                state = UNQUOTED
            pending = True
            i += 1
        elif state == UNQUOTED:
            if ch == ',':
                record.append(''.join(field))
                field = []
                state = START
            else:
                # Quotes here have no special meaning.
                field.append(ch)
            pending = True
            i += 1
        else:  # AFTER_QUOTE
            if ch == ',':
                record.append(''.join(field))
                field = []
                state = START
                pending = True
                i += 1
            else:
                raise ValueError(
                    "unexpected character {!r} after closing quote".format(ch)
                )

    if state == QUOTED:
        raise ValueError("unterminated quoted field")

    # Flush the final record, unless the input ended exactly on a record
    # boundary (or was empty).
    if pending:
        record.append(''.join(field))
        records.append(record)

    return records
