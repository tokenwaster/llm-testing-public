def parse_csv(text: str) -> list[list[str]]:
    """
    Parses an RFC-4180-style CSV string from scratch.
    """
    if not text:
        return []

    records = []
    current_record = []
    current_field = []
    i = 0
    n = len(text)
    state = "START_FIELD"

    while i < n or state == "POST_QUOTE":
        if i >= n:
            # If we reach the end of text, finalize any pending field/record.
            if state == "POST_QUOTE":
                # This case is handled by the loop condition and logic below.
                pass
            elif state in ("START_FIELD", "UNQUOTED_FIELD", "QUOTED_FIELD"):
                pass
            break

        char = text[i]

        if state == "START_FIELD":
            if char == '"':
                state = "QUOTED_FIELD"
                current_field = []
            elif char == ',':
                current_record.append("")
                # We are still in START_FIELD for the next field.
            elif char == '\n' or char == '\r':
                current_record.append("")
                records.append(current_record)
                current_record = []
                state = "START_FIELD"
                if char == '\r' and i + 1 < n and text[i+1] == '\n':
                    i += 1
            else:
                state = "UNQUOTED_FIELD"
                current_field = [char]
            i += 1

        elif state == "UNQUOTED_FIELD":
            if char == ',':
                current_record.append("".join(current_field))
                current_field = []
                state = "START_FIELD"
            elif char == '\n' or char == '\r':
                current_record.append("".join(current_field))
                records.append(current_record)
                current_record = []
                state = "START_FIELD"
                if char == '\r' and i + 1 < n and text[i+1] == '\n':
                    i += 1
            else:
                current_field.append(char)
            i += 1

        elif state == "QUOTED_FIELD":
            if char == '"':
                # Check for doubled quotes (escaped quote).
                if i + 1 < n and text[i+1] == '"':
                    current_field.append('"')
                    i += 2
                else:
                    state = "POST_QUOTE"
                    # Skip the closing quote itself.
                    i += 1
            else:
                current_field.append(char)
                i += 1

        elif state == "POST_QUOTE":
            if char in (',', '\n', '\r'):
                current_record.append("".join(current_field))
                if char == ',':
                    state = "START_FIELD"
                    i += 1
                else:  # \n or \r
                    records.append(current_record)
                    current_record = []
                    state = "START_FIELD"
                    if char == '\r' and i + 1 < n and text[i+1] == '\n':
                        i += 2
                    else:
                        i += 1
            else:
                # Characters after a closing quote that aren't comma, newline, or EOF.
                raise ValueError("Malformed input: characters after closing quote")

    # Final cleanup for the end of the string.
    if state == "UNQUOTED_FIELD":
        current_record.append("".join(current_field))
        records.append(current_record)
    elif state == "QUOTED_FIELD":
        raise ValueError("Malformed input: unclosed quote")
    elif state == "POST_QUOTE":
        current_record.append("".join(current_field))
        records.append(current_record)
    elif state == "START_FIELD" and current_record:
        # Handles cases where the string ends with a comma (e.g., 'a,').
        current_record.append("")
        records.append(current_record)

    return records
