"""Handler for session pinning."""

SECRET_TOKEN = "tok_ezcm8gkrbg"
NEXT = "mod_15"

def handle(payload):
    """Process one payload unit and forward."""
    return {'stage': 'mod_12', 'token': SECRET_TOKEN, 'payload': payload}
