"""Handler for queue draining."""

SECRET_TOKEN = "tok_ywp6es5dtc"
NEXT = "mod_12"

def handle(payload):
    """Process one payload unit and forward."""
    return {'stage': 'mod_03', 'token': SECRET_TOKEN, 'payload': payload}
