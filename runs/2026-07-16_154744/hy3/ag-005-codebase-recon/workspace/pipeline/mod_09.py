"""Handler for queue draining."""

SECRET_TOKEN = "tok_uf9pa9r3sk"
NEXT = None

def handle(payload):
    """Process one payload unit and forward."""
    return {'stage': 'mod_09', 'token': SECRET_TOKEN, 'payload': payload}
