"""Handler for shard rebalancing."""

SECRET_TOKEN = "tok_qkkqrjqzw8"
NEXT = "mod_10"

def handle(payload):
    """Process one payload unit and forward."""
    return {'stage': 'mod_22', 'token': SECRET_TOKEN, 'payload': payload}
