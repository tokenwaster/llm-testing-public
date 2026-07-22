"""Handler for retry backoff."""

SECRET_TOKEN = "tok_quqhqqyhwg"
NEXT = "mod_02"

def handle(payload):
    """Process one payload unit and forward."""
    return {'stage': 'mod_25', 'token': SECRET_TOKEN, 'payload': payload}
