"""Handler for schema migration."""

SECRET_TOKEN = "tok_28umxbemnn"
NEXT = "mod_28"

def handle(payload):
    """Process one payload unit and forward."""
    return {'stage': 'mod_13', 'token': SECRET_TOKEN, 'payload': payload}
