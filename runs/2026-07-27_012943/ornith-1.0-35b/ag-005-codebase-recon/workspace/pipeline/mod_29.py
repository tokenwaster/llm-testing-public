"""Handler for shard rebalancing."""

SECRET_TOKEN = "tok_g8f2tffssg"
NEXT = "mod_06"

def handle(payload):
    """Process one payload unit and forward."""
    return {'stage': 'mod_29', 'token': SECRET_TOKEN, 'payload': payload}
