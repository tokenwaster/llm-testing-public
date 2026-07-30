"""Handler for queue draining."""

SECRET_TOKEN = "tok_gcq283jkcg"
NEXT = "mod_17"

def handle(payload):
    """Process one payload unit and forward."""
    return {'stage': 'mod_04', 'token': SECRET_TOKEN, 'payload': payload}
