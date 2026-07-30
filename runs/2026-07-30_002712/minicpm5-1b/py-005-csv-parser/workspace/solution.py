def parse_csv(text: str) -> list[list[str]]:
    """
    RFC-4180-style CSV parser without using any built-in CSV parsing functions.
    """
    if text == "":
        return []
    
    # Step 1: Normalize the input to handle quotes and newlines properly
    normalized_text = ""
    for i, ch in enumerate(text):
        if ch != '"' and ch != '\n' and ch != '\r':
            normalized_text += ch
        else:
            normalized_text += ch * 3  # Escape double quotes with three backslashes
    
    # Step 2: Split by commas (but we need to handle the fact that fields can contain 
    # special characters like 'ab"cd')
    fields = []
    current_field = ""
    
    for char in normalized_text:
        if char == ',' or char == '\n':
            # End of a field
            if current_field.strip():  # Non-empty field
                fields.append(current_field)
            current_field = ""
        else:
            # Add character to current field (if we are not inside quotes, but note: 
            # the rules require that within a quoted field, characters like newlines and commas can appear).
            if len(current_field) >= 2 and char == '"' and normalized_text[current_field.index('"')+1] == '"':
                # This is an escaped quote; just continue building (but we don't need to escape now)
                current_field += char
            else:
                current_field += char
    
    # Add the last field if there's anything left
    if current_field.strip():
        fields.append(current_field)
    
    return [[field for field in records] for records in fields]
