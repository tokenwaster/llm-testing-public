Extract the order details from the email below into a single JSON object with EXACTLY these keys and value types:

- `order_id` (string)
- `customer_name` (string)
- `item_count` (integer)
- `total_usd` (number)
- `express` (boolean — whether express shipping was requested)

Output only the JSON object. Do not add any other keys, commentary, or code fences.

Email:
"Hi, this is Dana Whitfield. My order #A-4471 came to $128.50 for 3 items. Please use express shipping. Thanks!"
