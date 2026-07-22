"""Handler for feature flags."""

SECRET_TOKEN = "tok_34477wkfzr"
NEXT = "mod_24"

def handle(payload):
    """Process one payload unit and forward."""
    return {'stage': 'mod_21', 'token': SECRET_TOKEN, 'payload': payload}
