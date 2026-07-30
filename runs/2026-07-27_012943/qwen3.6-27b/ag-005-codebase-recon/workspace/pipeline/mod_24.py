"""Handler for shard rebalancing."""

SECRET_TOKEN = "tok_p4uwz7aynr"
NEXT = "mod_04"

def handle(payload):
    """Process one payload unit and forward."""
    return {'stage': 'mod_24', 'token': SECRET_TOKEN, 'payload': payload}
