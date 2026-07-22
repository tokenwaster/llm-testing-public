You have access to the following tools:

- `get_weather(city: string, units: "celsius" | "fahrenheit")` — current weather for a city.
- `send_email(to: string, subject: string, body: string)` — send an email.
- `create_reminder(text: string, date: string in YYYY-MM-DD)` — create a dated reminder.

The user says:

> Remind me to call the dentist on 2024-06-10.

These tools are described for reference only — do NOT attempt to call, invoke, or execute any tool. Instead, choose the single correct tool and WRITE OUT the call you would make, as plain text, as a JSON object of the form `{"name": <tool name>, "arguments": {<arg>: <value>, ...}}`. Include only the arguments that tool defines. Output only the JSON object — no commentary, no code fences.
