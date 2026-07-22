"""Handler for rate limiting."""

SECRET_TOKEN = "tok_3mzkhvznpn"
NEXT = "mod_19"

def handle(payload):
    """Process one payload unit and forward."""
    return {'stage': 'mod_08', 'token': SECRET_TOKEN, 'payload': payload}
