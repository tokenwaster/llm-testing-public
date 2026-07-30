"""A from-scratch RFC-4180-style CSV parser.

The grammar handled here:
  * fields are separated by commas;
  * records are separated by '\n' or '\r\n';
  * a field that *starts* with a double quote may contain commas, newlines
    and escaped quotes ('""' decodes to a single '"');
  * a quote anywhere else is an ordinary character;
  * a closing quote must be followed by a comma, a newline, or end-of-input.
"""


def parse_csv(text: str) -> list[list[str]]:
    """Parse *text* as CSV and return a list of records.

    Each record is a list of field strings.  Raises ValueError on malformed
    input: an unterminated quoted field, or unexpected characters after a
    closing quote.
    """
    records: list[list[str]] = []
    fields: list[str] = []
    buf: list[str] = []

    START, UNQUOTED, QUOTED, AFTER_QUOTE = range(4)
    state = START

    i = 0
    n = len(text)

    def end_field() -> None:
        nonlocal buf
        fields.append("".join(buf))
        buf = []

    def end_record() -> None:
        nonlocal fields
        end_field()
        records.append(fields)
        fields = []

    while i < n:
        c = text[i]

        if state == QUOTED:
            if c == '"':
                if i + 1 < n and text[i + 1] == '"':
                    buf.append('"')  # '""' is an escaped literal quote
                    i += 2
                else:
                    state = AFTER_QUOTE
                    i += 1
            else:
                buf.append(c)  # commas/newlines are data inside quotes
                i += 1
            continue

        if state == AFTER_QUOTE:
            if c == ",":
                end_field()
                state = START
                i += 1
            elif c == "\n":
                end_record()
                state = START
                i += 1
            elif c == "\r" and i + 1 < n and text[i + 1] == "\n":
                end_record()
                state = START
                i += 2
            else:
                raise ValueError(
                    f"unexpected character {c!r} after closing quote"
                )
            continue

        # START or UNQUOTED: delimiters behave identically in both states
        # (buf is empty in START).  A quote is special only in START.
        if state == START and c == '"':
            state = QUOTED
            i += 1
        elif c == ",":
            end_field()
            state = START
            i += 1
        elif c == "\n":
            end_record()
            state = START
            i += 1
        elif c == "\r" and i + 1 < n and text[i + 1] == "\n":
            end_record()
            state = START
            i += 2
        else:
            # Includes a bare '\r' not followed by '\n': treated as data.
            buf.append(c)
            state = UNQUOTED
            i += 1

    if state == QUOTED:
        raise ValueError("unterminated quoted field")

    if state in (UNQUOTED, AFTER_QUOTE):
        end_record()
    elif state == START and fields:
        # The input ended immediately after a comma, so one last empty
        # field (and its record) is still pending.  If the input instead
        # ended with a newline (or was empty), nothing is pending.
        end_record()

    return records
