def parse_csv(text: str) -> list[list[str]]:
    if text == "":
        return []
    
    # Normalize \r\n to \n for easier processing... 
    # Actually, we need to be careful: quoted fields can contain \r\n
    # Let's work with the raw text character by character
    
    records = []
    current_record = []
    current_field = []
    i = 0
    n = len(text)
    
    while i < n:
        c = text[i]
        
        # Start of a field
        if c == '"':
            # Quoted field
            i += 1  # skip opening quote
            while True:
                if i >= n:
                    raise ValueError("Unclosed quoted field")
                c = text[i]
                if c == '"':
                    # Check if it's an escaped quote ""
                    if i + 1 < n and text[i + 1] == '"':
                        current_field.append('"')
                        i += 2
                    else:
                        # Closing quote
                        i += 1  # skip closing quote
                        # After closing quote, expect comma, newline, or EOF
                        if i >= n:
                            # EOF - valid
                            break
                        elif text[i] == ',':
                            break
                        elif text[i] == '\n':
                            break
                        elif text[i] == '\r' and i + 1 < n and text[i + 1] == '\n':
                            break
                        elif text[i] == '\r':
                            # treat lone \r as newline? RFC 4180 says \r\n
                            # Let's treat \r alone as a record separator too
                            break
                        else:
                            raise ValueError(f"Character after closing quote: {text[i]!r}")
                elif c == '\r':
                    if i + 1 < n and text[i + 1] == '\n':
                        current_field.append('\r\n')
                        i += 2
                    else:
                        current_field.append('\r')
                        i += 1
                else:
                    current_field.append(c)
                    i += 1
            
            current_record.append(''.join(current_field))
            current_field = []
            
            # Now handle what comes after the closing quote
            if i >= n:
                # EOF
                records.append(current_record)
                current_record = []
            elif text[i] == ',':
                i += 1  # skip comma, next iteration starts next field
            elif text[i] == '\n':
                i += 1
                records.append(current_record)
                current_record = []
            elif text[i] == '\r' and i + 1 < n and text[i + 1] == '\n':
                i += 2
                records.append(current_record)
                current_record = []
            elif text[i] == '\r':
                i += 1
                records.append(current_record)
                current_record = []
        
        elif c == ',':
            # Empty field
            current_record.append('')
            i += 1
        
        elif c == '\n':
            # End of record
            current_record.append(''.join(current_field))
            current_field = []
            records.append(current_record)
            current_record = []
            i += 1
        
        elif c == '\r':
            if i + 1 < n and text[i + 1] == '\n':
                i += 2
            else:
                i += 1
            current_record.append(''.join(current_field))
            current_field = []
            records.append(current_record)
            current_record = []
        
        else:
            # Regular character
            current_field.append(c)
            i += 1
    
    # Handle any remaining content
    # If we have a current_field or current_record that isn't committed
    if current_field or current_record:
        current_record.append(''.join(current_field))
        records.append(current_record)
    elif current_record:
        records.append(current_record)
    
    # Remove trailing empty record caused by trailing newline
    # A trailing newline means the last character was \n or \r\n
    # In that case, we would have appended an empty record at the end
    # Check: if the input ends with \n or \r\n, and the last record is ['']
    # Actually, we need to re-examine our logic
    
    # The issue: when we hit \n, we do:
    #   current_record.append(current_field) -> appends ''
    #   records.append(current_record)
    #   reset current_record = []
    # Then loop ends with current_field=[], current_record=[]
    # So neither condition (current_field or current_record) triggers
    # That means trailing newline is handled correctly already!
    
    # But wait, what about the comma case? When c == ',' we append '' and move on
    # but don't append current_field to current_record. That's a bug.
    
    # Let me reconsider the approach - the comma handling is wrong above.
    # When we see a comma, we need to finalize the current field (which should be empty
    # since we just started a new field). But that's only for the case where
    # field starts with comma immediately.
    
    # Actually the logic is flawed. Let me rewrite more carefully.
    
    return records


def parse_csv(text: str) -> list[list[str]]:
    if text == "":
        return []
    
    records = []
    i = 0
    n = len(text)
    
    def parse_field():
        nonlocal i
        if i >= n:
            return ""
        
        c = text[i]
        
        if c == '"':
            # Quoted field
            i += 1
            field_chars = []
            while True:
                if i >= n:
                    raise ValueError("Unclosed quoted field")
                c = text[i]
                if c == '"':
                    if i + 1 < n and text[i + 1] == '"':
                        field_chars.append('"')
                        i += 2
                    else:
                        i += 1  # skip closing quote
                        # Verify next char is comma, newline, or EOF
                        if i < n and text[i] not in (',', '\n', '\r'):
                            raise ValueError(f"Unexpected character after closing quote: {text[i]!r}")
                        return ''.join(field_chars)
                elif c == '\r':
                    if i + 1 < n and text[i + 1] == '\n':
                        field_chars.append('\r\n')
                        i += 2
                    else:
                        field_chars.append('\r')
                        i += 1
                else:
                    field_chars.append(c)
                    i += 1
        else:
            # Unquoted field: read until comma, newline, or EOF
            field_chars = []
            while i < n and text[i] not in (',', '\n', '\r'):
                field_chars.append(text[i])
                i += 1
            return ''.join(field_chars)
    
    def parse_record():
        nonlocal i
        record = []
        while True:
            field = parse_field()
            record.append(field)
            if i >= n:
                return record, False  # no trailing newline / EOF
            c = text[i]
            if c == ',':
                i += 1
                continue
            elif c == '\n':
                i += 1
                return record, True
            elif c == '\r':
                if i + 1 < n and text[i + 1] == '\n':
                    i += 2
                else:
                    i += 1
                return record, True
            else:
                # Shouldn't happen
                return record, False
    
    while i < n:
        record, had_newline = parse_record()
        # If had_newline and this was the last thing and the record is ['']
        # and i >= n, it's a trailing newline
        if had_newline and i >= n and record == ['']:
            # trailing newline - don't add empty record
            # But only if records is not empty (i.e., there were previous records)
            # Actually, if the entire input is just "\n", parse_csv("\n") should return [['']].
            # Wait, let me re-read the rules:
            # "A trailing newline at the end of the input does not create an extra record"
            # So if input is "a\nb\n", result is [['a'], ['b']], not [['a'], ['b'], ['']]
            # But if input is "\n", is that a trailing newline with no content before? 
            # Hmm, "\n" - there's one record before the newline which is [''], so result should be [['']]
            # Actually no - "a trailing newline does not create an extra record"
            # So "\n" = one empty record followed by trailing newline = [['']]? 
            # Or is it just the trailing newline = []?
            # I think "\n" has one empty record [''] and then the trailing newline doesn't add another.
            # So result is [['']]
            # But if input is "a\n", result is [['a']]
            # And "a\n\n" would be [['a'], ['']] (the middle \n creates one empty record, trailing \n doesn't add)
            # Wait but we need to be careful: the trailing newline rule means:
            # after processing all records, if the last thing we did was consume a newline
            # and there's nothing after it, we should NOT add the empty record we'd get.
            # 
            # My current approach: parse_record always returns a record.
            # If had_newline=True and i>=n and record==[''], it's a trailing newline scenario.
            # But wait, "a\n" -> parse_record returns (['a'], True), i>=n, record!=[''], so add ['a']. Done.
            # "\n" -> parse_record returns ([''], True), i>=n, record==[''], so... 
            # The spec says trailing newline doesn't create extra record.
            # But "\n" IS just a trailing newline with an empty "record" before it.
            # Hmm. Let me think differently:
            # 
            # "a\n" is "a" followed by trailing newline -> [['a']]
            # "" -> []
            # "\n" -> Is the empty string before \n a record? Yes: [['']]
            # "a\n\n" -> [['a'], ['']]  (second \n is trailing newline after empty record)
            # 
            # So the rule is: if the input ends with a newline, don't add an extra empty record
            # BEYOND what's there. The "trailing newline" just means the last newline doesn't
            # produce an additional empty record.
            #
            # So: "a\n" -> records so far = [], then we parse 'a' with newline.
            # After consuming newline, i>=n, so the newline was the last char.
            # The record ['a'] is valid. No extra record is created.
            # So we add ['a'] and stop. Result: [['a']]. Correct.
            #
            # "\n" -> records so far = [], then we parse '' with newline.
            # After consuming newline, i>=n. record=[''].
            # Is this trailing newline? The record [''] has content (empty string field).
            # I think we should still add it. Result: [['']]
            # 
            # "a\nb\n" -> parse ['a'] (newline, i not at end), add. parse ['b'] (newline, i at end).
            # Add ['b']. Result: [['a'], ['b']]. Correct.
            #
            # So actually the "trailing newline" issue only occurs if:
            # the ENTIRE input ends with a newline, and we would have added an EXTRA empty record.
            # That extra record comes from: after the last real record's newline, there's another \n.
            # e.g., "a\n\n" -> parse ['a'] (newline), parse [''] (newline, i at end).
            # Without the rule, result would be [['a'], ['']].
            # With the rule... wait but the spec says "an empty line in the middle is one record 
            # containing a single empty field". So "a\n\n" should be [['a'], ['']]?
            # 
            # Let me re-read: "A trailing newline at the end of the input does not create an extra record,
            # but an empty line in the middle is one record containing a single empty field."
            #
            # So "a\n\n" has an empty line in the middle? No, \n\n means two newlines.
            # First \n ends 'a' record. Second \n is... trailing? Or is '' between the two \n's a record?
            # 
            # I think: "a\n\nb" -> [['a'], [''], ['b']] (empty line in middle)
            # "a\n\n" -> [['a'], ['']] ? Or [['a']] ?
            # 
            # The spec says trailing newline doesn't create extra record. So:
            # "a\n" -> [['a']] (trailing newline)
            # "a\nb\n" -> [['a'], ['b']] (trailing newline)
            # "a\n\n" -> [['a'], ['']] because the first \n ends 'a', then '' is a real empty record,
            #            then the second \n is the trailing newline. Result: [['a'], ['']]
            # 
            # So the rule is: if the input ends with exactly one newline (the very last char),
            # don't add an extra empty record for that newline.
            # My current approach handles this correctly EXCEPT for the edge case of "\n":
            # "\n" -> parse '' (newline, i at end). record=['']. 
            # If I skip this when record==[''] and i>=n, then "\n" -> [].
            # But what should "\n" be? 
            # "\n" = empty record followed by trailing newline?
            # The trailing newline doesn't create extra record.
            # The empty record before it DOES exist. So "\n" should be [['']]? 
            # Or is the whole "\n" just a trailing newline -> []?
            #
            # I think "\n" should give [['']] because the empty field is a real record,
            # and \n is the trailing newline.
            # But then "a\n" gives [['a']] by same logic: 'a' is real record, \n is trailing.
            # 
            # Hmm but then "\n\n" would give [['']] (first \n separates empty record from empty record,
            # but the second \n is trailing). No wait, "\n\n":
            # Parse '': hit first \n, i points to second \n.
            # record=[''], had_newline=True, i not at end (second \n remains).
            # Add ['']. 
            # Parse '': hit second \n, i at end. record=[''], had_newline=True, i>=n.
            # This is the trailing newline case. Skip.
            # Result: [['']]. 
            # That seems right: "\n\n" is empty line in middle + trailing newline = [['']]
            #
            # And "\n" -> parse '' + first \n, i at end. record=[''], had_newline=True, i>=n.
            # If we DON'T skip this, result is [['']] which seems right 
            # (the empty record before the trailing newline).
            # Wait but "a\n" also goes through: parse 'a' + \n, i at end. 
            # record=['a'], had_newline=True, i>=n. We add it -> [['a']]. 
            # So the ONLY case to skip is when we have an empty record... but we'd be skipping
            # empty records that might be legitimate.
            #
            # Actually I think the intent of the trailing newline rule is simpler:
            # Standard CSV files end with \n. That \n doesn't add an empty row.
            # So "a,b\nc,d\n" -> [['a','b'], ['c','d']], not [['a','b'], ['c','d'], ['']]
            #
            # The problematic case is only when after consuming a newline, there's NOTHING left
            # and the record we're about to add is empty [''].
            # "a,b\nc,d\n" -> after 'c,d\n', record=['c','d'], not empty, so add it. Good.
            # "a\n\n" -> first: record=['a'], not empty, add. second: record=[''], empty, i>=n -> skip? 
            # But spec says "an empty line in the middle is one record". The second \n IS trailing.
            # But is the '' between the two \n's "in the middle"?
            # 
            # I think the correct interpretation of trailing newline is:
            # If input ends with \n, strip that last \n before parsing.
            # So preprocess: if text ends with \r\n, strip those 2; elif ends with \n, strip 1.
            # Then parse.
            #
            # Let me just do that preprocessing approach instead.
            pass
        records.append(record)
    
    return records


def parse_csv(text: str) -> list[list[str]]:
    if text == "":
        return []
    
    # Strip trailing newline (one, if present)
    if text.endswith('\r\n'):
        text = text[:-2]
    elif text.endswith('\n'):
        text = text[:-1]
    elif text.endswith('\r'):
        text = text[:-1]
    
    if text == "":
        return []
    
    records = []
    i = 0
    n = len(text)
    
    def parse_field():
        nonlocal i
        if i >= n:
            return ""
        
        c = text[i]
        
        if c == '"':
            # Quoted field
            i += 1
            field_chars = []
            while True:
                if i >= n:
                    raise ValueError("Unclosed quoted field")
                c = text[i]
                if c == '"':
                    if i + 1 < n and text[i + 1] == '"':
                        field_chars.append('"')
                        i += 2
                    else:
                        i += 1  # skip closing quote
                        # Verify next char is comma, newline, or EOF
                        if i < n and text[i] not in (',', '\n', '\r'):
                            raise ValueError(f"Unexpected character after closing quote: {text[i]!r}")
                        return ''.join(field_chars)
                elif c == '\r':
                    if i + 1 < n and text[i + 1] == '\n':
                        field_chars.append('\r\n')
                        i += 2
                    else:
                        field_chars.append('\r')
                        i += 1
                else:
                    field_chars.append(c)
                    i += 1
        else:
            # Unquoted field: read until comma, newline, or EOF
            field_chars = []
            while i < n and text[i] not in (',', '\n', '\r'):
                field_chars.append(text[i])
                i += 1
            return ''.join(field_chars)
    
    while i < n:
        record = []
        while True:
            field = parse_field()
            record.append(field)
            if i >= n:
                break
            c = text[i]
            if c == ',':
                i += 1
                continue
            elif c == '\n':
                i += 1
                break
            elif c == '\r':
                if i + 1 < n and text[i + 1] == '\n':
                    i += 2
                else:
                    i += 1
                break
        records.append(record)
    
    return records
