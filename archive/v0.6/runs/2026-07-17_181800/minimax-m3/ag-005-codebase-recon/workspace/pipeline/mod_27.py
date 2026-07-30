"""Handler for queue draining."""

SECRET_TOKEN = "tok_t9abg9f8rr"
NEXT = "mod_20"

def handle(payload):
    """Process one payload unit and forward."""
    return {'stage': 'mod_27', 'token': SECRET_TOKEN, 'payload': payload}
