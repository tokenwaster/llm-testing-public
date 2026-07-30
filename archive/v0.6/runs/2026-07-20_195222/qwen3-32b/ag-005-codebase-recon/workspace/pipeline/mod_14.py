"""Handler for retry backoff."""

SECRET_TOKEN = "tok_8ewxh6ha72"
NEXT = "mod_00"

def handle(payload):
    """Process one payload unit and forward."""
    return {'stage': 'mod_14', 'token': SECRET_TOKEN, 'payload': payload}
