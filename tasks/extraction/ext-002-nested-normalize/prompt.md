From the order log below, produce a single JSON object of the form:

```
{"orders": [ {"order_id": ..., "date": ..., "amount_usd": ..., "customer": ..., "paid": ...}, ... ]}
```

Rules:
- **One entry per unique `order_id`.** An order may be mentioned more than once; merge all mentions of the same id into a single entry, combining the fields given across those mentions.
- `date` normalized to ISO `YYYY-MM-DD`.
- `amount_usd` is a number (no symbols), or `null` if never stated.
- `paid` is a boolean, or `null` if the payment status is never stated. Do not guess.
- `customer` is the name, or `null` if never stated.
- Sort the array by `date`, ascending.
- Output only the JSON object — no commentary, no code fences.

Order log:
"- Order X-10 placed 2023-04-05, total $120. Customer: Ana.
- Order X-9, Jan 3 2023, $85.50, paid. Customer: Ben.
- Order X-10 update: shipped, tracking TRK-77 (paid in full).
- Order X-11 (03/28/2023) for Ana, amount not given, unpaid.
- Order X-9: phone order, customer Ben."
