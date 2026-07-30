You have access to the following tools:

- `search_contacts(name: string)` — returns the contact records (each with an `id`) matching a name.
- `send_message(contact_id: string, text: string)` — send a message to a contact by their id.
- `get_weather(city: string)` — current weather for a city.

The user says:

> Text Jordan that I'll be 10 minutes late.

These tools are described for reference only — do NOT attempt to call, invoke, or execute any tool. Instead, WRITE OUT, as plain text, the JSON for the **single next tool call** that should be made right now, as `{"name": <tool>, "arguments": {...}}`.

Rules:
- Never invent an argument value. If a required argument's value is not known yet because it would come from another tool's result, that call cannot be made yet — write the call that obtains it instead.
- Output only the JSON object — no commentary, no code fences.
