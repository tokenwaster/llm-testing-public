#!/usr/bin/env python3
"""
RFC-4180 style CSV parser implemented from scratch.
"""

from typing import List


def parse_csv(text: str) -> List[List[str]]:
    """
    Parse a string containing RFC‑4180 CSV data and return a list of records,
    each record being a list of fields.

    Raises ValueError on malformed input.
    """
    if text == "":
        return []

    # Normalize line endings to '\n' for easier processing
    # but keep original positions for error messages if needed
    lines = []
    i = 0
    n = len(text)
    while i < n:
        if text[i] == "\r":
            if i + 1 < n and text[i + 1] == "\n":
                lines.append(text[:i])
                text = text[i + 2 :]
                i = 0
                n = len(text)
            else:
                # lone '\r' treated as newline
                lines.append(text[:i])
                text = text[i + 1 :]
                i = 0
                n = len(text)
        elif text[i] == "\n":
            lines.append(text[:i])
            text = text[i + 1 :]
            i = 0
            n = len(text)
        else:
            i += 1

    # After loop, if any remaining text (no trailing newline), add it
    if text != "":
        lines.append(text)

    records: List[List[str]] = []

    for line in lines:
        fields: List[str] = []
        idx = 0
        length = len(line)
        while idx <= length:
            # End of record reached
            if idx == length:
                fields.append("")
                break

            ch = line[idx]
            if ch == ",":
                # Empty field before comma
                fields.append("")
                idx += 1
                continue

            if ch == '"':
                # Quoted field
                idx += 1
                start = idx
                buf = []
                while True:
                    if idx >= length:
                        raise ValueError("Unclosed quoted field")
                    c = line[idx]
                    if c == '"':
                        # Check for escaped quote
                        if idx + 1 < length and line[idx + 1] == '"':
                            buf.append('"')
                            idx += 2
                        else:
                            idx += 1
                            break
                    else:
                        buf.append(c)
                        idx += 1

                field = "".join(buf)

                # After closing quote, expect comma or end of record
                if idx < length and line[idx] != ",":
                    raise ValueError("Invalid character after quoted field")
                fields.append(field)

                if idx == length:
                    break
                else:  # comma
                    idx += 1
                    continue

            else:
                # Unquoted field
                start = idx
                while idx < length and line[idx] != ",":
                    idx += 1
                field = line[start:idx]
                fields.append(field)
                if idx == length:
                    break
                else:  # comma
                    idx += 1
                    continue

        records.append(fields)

    return records


# If run as a script, demonstrate usage with simple tests
if __name__ == "__main__":
    import sys

    sample = 'a,b,"c,d",e\n"f\ng","h""i",j'
    print(parse_csv(sample))
