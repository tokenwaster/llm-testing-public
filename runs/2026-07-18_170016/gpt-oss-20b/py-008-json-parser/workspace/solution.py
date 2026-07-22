#!/usr/bin/env python3
"""
A minimal JSON parser that follows the full JSON grammar.
It returns the corresponding Python object or None if the input is invalid.
"""

import sys

def parse(text: str):
    """Parse a JSON document and return the equivalent Python object,
    or None if the input is not valid JSON."""
    # Use a mutable index wrapped in a list to allow updates inside nested functions
    idx = [0]
    length = len(text)

    def skip_whitespace():
        while idx[0] < length and text[idx[0]] in ' \t\n\r':
            idx[0] += 1

    def parse_value():
        skip_whitespace()
        if idx[0] >= length:
            return None
        ch = text[idx[0]]
        if ch == '{':
            return parse_object()
        elif ch == '[':
            return parse_array()
        elif ch == '"':
            return parse_string()
        elif ch == 't' or ch == 'f' or ch == 'n':
            return parse_literal()
        elif ch == '-' or ch.isdigit():
            return parse_number()
        else:
            return None

    def parse_object():
        # assume current char is '{'
        idx[0] += 1
        skip_whitespace()
        obj = {}
        if idx[0] < length and text[idx[0]] == '}':
            idx[0] += 1
            return obj
        while True:
            skip_whitespace()
            if idx[0] >= length or text[idx[0]] != '"':
                return None
            key = parse_string()
            if key is None:
                return None
            skip_whitespace()
            if idx[0] >= length or text[idx[0]] != ':':
                return None
            idx[0] += 1
            val = parse_value()
            if val is None and not isinstance(val, bool) and val is not None:
                # parse_value returns None only on error; but False/True are valid.
                return None
            obj[key] = val
            skip_whitespace()
            if idx[0] >= length:
                return None
            ch = text[idx[0]]
            if ch == '}':
                idx[0] += 1
                break
            elif ch == ',':
                idx[0] += 1
                continue
            else:
                return None
        return obj

    def parse_array():
        # assume current char is '['
        idx[0] += 1
        skip_whitespace()
        arr = []
        if idx[0] < length and text[idx[0]] == ']':
            idx[0] += 1
            return arr
        while True:
            val = parse_value()
            if val is None and not isinstance(val, bool) and val is not None:
                return None
            arr.append(val)
            skip_whitespace()
            if idx[0] >= length:
                return None
            ch = text[idx[0]]
            if ch == ']':
                idx[0] += 1
                break
            elif ch == ',':
                idx[0] += 1
                continue
            else:
                return None
        return arr

    def parse_string():
        # assume current char is '"'
        idx[0] += 1
        start = idx[0]
        s_chars = []
        while idx[0] < length:
            ch = text[idx[0]]
            if ch == '"':
                idx[0] += 1
                return ''.join(s_chars)
            elif ch == '\\':
                idx[0] += 1
                if idx[0] >= length:
                    return None
                esc = text[idx[0]]
                if esc == '"' or esc == '\\' or esc == '/':
                    s_chars.append(esc)
                elif esc == 'b':
                    s_chars.append('\b')
                elif esc == 'f':
                    s_chars.append('\f')
                elif esc == 'n':
                    s_chars.append('\n')
                elif esc == 'r':
                    s_chars.append('\r')
                elif esc == 't':
                    s_chars.append('\t')
                elif esc == 'u':
                    # parse 4 hex digits
                    if idx[0] + 4 >= length:
                        return None
                    hex_digits = text[idx[0]+1:idx[0]+5]
                    try:
                        codepoint = int(hex_digits, 16)
                        s_chars.append(chr(codepoint))
                    except ValueError:
                        return None
                    idx[0] += 4
                else:
                    return None
            elif ord(ch) < 0x20:
                # control characters not allowed in JSON strings
                return None
            else:
                s_chars.append(ch)
            idx[0] += 1
        return None

    def parse_literal():
        if text.startswith('true', idx[0]):
            idx[0] += 4
            return True
        elif text.startswith('false', idx[0]):
            idx[0] += 5
            return False
        elif text.startswith('null', idx[0]):
            idx[0] += 4
            return None
        else:
            return None

    def parse_number():
        start = idx[0]
        if text[idx[0]] == '-':
            idx[0] += 1
            if idx[0] >= length or not text[idx[0]].isdigit():
                return None
        # integer part
        if text[idx[0]] == '0':
            idx[0] += 1
            if idx[0] < length and text[idx[0]].isdigit():
                return None  # leading zeros not allowed
        else:
            while idx[0] < length and text[idx[0]].isdigit():
                idx[0] += 1
        # fraction part
        is_float = False
        if idx[0] < length and text[idx[0]] == '.':
            is_float = True
            idx[0] += 1
            if idx[0] >= length or not text[idx[0]].isdigit():
                return None
            while idx[0] < length and text[idx[0]].isdigit():
                idx[0] += 1
        # exponent part
        if idx[0] < length and (text[idx[0]] == 'e' or text[idx[0]] == 'E'):
            is_float = True
            idx[0] += 1
            if idx[0] < length and (text[idx[0]] == '+' or text[idx[0]] == '-'):
                idx[0] += 1
            if idx[0] >= length or not text[idx[0]].isdigit():
                return None
            while idx[0] < length and text[idx[0]].isdigit():
                idx[0] += 1
        num_str = text[start:idx[0]]
        try:
            if is_float:
                return float(num_str)
            else:
                return int(num_str)
        except ValueError:
            return None

    result = parse_value()
    skip_whitespace()
    if idx[0] != length or result is None and not isinstance(result, bool):
        # trailing garbage or error
        return None
    return result


# If run as a script, provide simple CLI for testing
if __name__ == "__main__":
    import json
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            txt = f.read()
        out = parse(txt)
        print(out)
    else:
        # Read from stdin
        txt = sys.stdin.read()
        out = parse(txt)
        print(out)
