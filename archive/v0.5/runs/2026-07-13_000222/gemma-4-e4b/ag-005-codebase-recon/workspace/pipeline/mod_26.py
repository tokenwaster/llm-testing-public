"""Handler for feature flags."""

SECRET_TOKEN = "tok_wd6a4xmqmf"
NEXT = "mod_23"

def handle(payload):
    """Process one payload unit and forward."""
    return {'stage': 'mod_26', 'token': SECRET_TOKEN, 'payload': payload}
