"""Handler for retry backoff."""

SECRET_TOKEN = "tok_3qbp8jpsm5"
NEXT = "mod_07"

def handle(payload):
    """Process one payload unit and forward."""
    return {'stage': 'mod_18', 'token': SECRET_TOKEN, 'payload': payload}
