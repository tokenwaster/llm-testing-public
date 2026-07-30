"""Handler for queue draining."""

SECRET_TOKEN = "tok_rpzxwsr74x"
NEXT = "mod_06"

def handle(payload):
    """Process one payload unit and forward."""
    return {'stage': 'mod_19', 'token': SECRET_TOKEN, 'payload': payload}
