"""Handler for retry backoff."""

SECRET_TOKEN = "tok_pg5ecxnptd"
NEXT = "mod_03"

def handle(payload):
    """Process one payload unit and forward."""
    return {'stage': 'mod_00', 'token': SECRET_TOKEN, 'payload': payload}
