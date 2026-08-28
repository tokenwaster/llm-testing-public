def parse_csv(text: str) -> list[list[str]]:
    """Parse RFC-4180-style CSV text into a list of records (lists of fields).

    Rules implemented:
      * Fields are separated by commas; records by LF or CRLF.
      * A field that starts with a double quote is a quoted field: it may
        contain commas, newlines, and doubled quotes ('""' decodes to '"').
      * A quote that does not start a field is an ordinary character.
      * A trailing newline does not create an extra record; an empty line in
        the middle of the input is one record with a single empty field.
      * Malformed input (an unclosed quote, or characters after a closing
        quote that are not a comma/newline/EOF) raises ValueError.
    """
    records: list[list[str]] = []
    i = 0
    n = len(text)

    while i < n:  # one iteration per record
        fields: list[str] = []

        while True:  # one iteration per field
            if i < n and text[i] == '"':
                # --- Quoted field (quote is special only at field start) ---
                field_start = i
                i += 1  # consume the opening quote
                buf: list[str] = []
                closed = False
                while i < n:
                    c = text[i]
                    if c == '"':
                        if i + 1 < n and text[i + 1] == '"':
                            buf.append('"')  # '""' decodes to one '"'
                            i += 2
                        else:
                            i += 1  # consume the closing quote
                            closed = True
                            break
                    else:
                        # Commas and newlines are literal inside quotes.
                        buf.append(c)
                        i += 1
                if not closed:
                    raise ValueError(
                        "malformed CSV: unterminated quoted field "
                        f"(opening quote at position {field_start})"
                    )
                fields.append("".join(buf))
            else:
                # --- Unquoted field ---
                # Quotes are only special at the very start of a field, so
                # any quote seen here is an ordinary character.  The field
                # ends at a comma or a record separator ('\n' or '\r\n');
                # a '\r' not followed by '\n' is an ordinary character.
                start = i
                while i < n:
                    c = text[i]
                    if c == "," or c == "\n":
                        break
                    if c == "\r" and i + 1 < n and text[i + 1] == "\n":
                        break
                    i += 1
                fields.append(text[start:i])

            # --- After a field: comma, record separator, or EOF ---
            if i >= n:
                break  # end of input also ends the record
            c = text[i]
            if c == ",":
                i += 1
                continue  # parse the next field of this record
            if c == "\n":
                i += 1
                break  # record finished
            if c == "\r" and i + 1 < n and text[i + 1] == "\n":
                i += 2
                break  # record finished
            # Only reachable just after a closing quote (the unquoted scan
            # never stops at a bare '\r'): junk after the closing quote.
            raise ValueError(
                "malformed CSV: unexpected character "
                f"{text[i]!r} after closing quote (position {i})"
            )

        records.append(fields)

    return records
