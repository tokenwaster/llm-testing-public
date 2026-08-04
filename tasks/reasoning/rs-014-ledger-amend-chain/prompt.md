Below is an append-only audit log for a set of accounts. Apply the
entries **in the order written**, top to bottom.

- `POST <id> | <account> | credit N` adds N to that account. `debit N`
  subtracts N. A posting starts out counting.
- `AMEND <id> | amount := M` replaces that entry's amount with M. The account
  and the credit/debit direction never change. An entry may be amended more
  than once; the last amendment before the end is the one that counts.
- `VOID <id>` stops that entry counting.
- `RESTORE <id>` makes it count again. A restored entry keeps whatever amount
  it has at that moment, and it can be voided again afterwards.

An entry counts towards the final balance only if the **last** `VOID` or
`RESTORE` affecting it is a `RESTORE`, or if it was never voided at all.

What is the final balance of **AC-118**? Give the integer; it may be
negative.

--- BEGIN LOG ---
POST    T104 | AC-451 | credit 297
POST    T112 | AC-118 | credit 694
POST    T117 | AC-118 | debit 423
POST    T121 | AC-118 | debit 386
POST    T130 | AC-118 | credit 184
POST    T139 | AC-377 | credit 30
POST    T147 | AC-118 | debit 48
POST    T149 | AC-118 | debit 433
POST    T160 | AC-377 | credit 676
POST    T168 | AC-451 | debit 205
POST    T170 | AC-377 | credit 297
POST    T180 | AC-377 | debit 532
POST    T186 | AC-118 | credit 305
POST    T193 | AC-118 | credit 778
POST    T201 | AC-118 | credit 455
POST    T208 | AC-204 | debit 486
POST    T214 | AC-118 | debit 447
POST    T223 | AC-377 | debit 423
POST    T227 | AC-118 | debit 88
POST    T237 | AC-118 | debit 605
POST    T243 | AC-118 | debit 453
POST    T247 | AC-118 | debit 502
POST    T256 | AC-118 | credit 63
POST    T266 | AC-377 | credit 417
POST    T268 | AC-118 | debit 45
POST    T275 | AC-377 | debit 277
POST    T282 | AC-118 | credit 813
POST    T290 | AC-118 | debit 532
POST    T298 | AC-118 | credit 638
POST    T308 | AC-377 | debit 52
POST    T314 | AC-451 | credit 540
POST    T322 | AC-377 | debit 413
POST    T325 | AC-451 | debit 519
POST    T335 | AC-118 | debit 500
POST    T340 | AC-118 | credit 153
POST    T346 | AC-118 | credit 236
POST    T354 | AC-118 | credit 577
POST    T362 | AC-118 | credit 282
POST    T371 | AC-118 | debit 448
POST    T374 | AC-118 | credit 170
POST    T385 | AC-118 | credit 704
POST    T388 | AC-451 | debit 629
POST    T399 | AC-451 | credit 611
POST    T404 | AC-118 | debit 350
POST    T408 | AC-204 | credit 90
VOID    T170
VOID    T354
AMEND   T193 | amount := 374
AMEND   T201 | amount := 308
VOID    T335
AMEND   T112 | amount := 137
RESTORE T282
RESTORE T298
AMEND   T130 | amount := 103
VOID    T282
VOID    T149
AMEND   T256 | amount := 281
AMEND   T247 | amount := 853
VOID    T117
RESTORE T335
AMEND   T374 | amount := 44
VOID    T371
VOID    T290
AMEND   T180 | amount := 298
VOID    T362
VOID    T268
VOID    T227
AMEND   T371 | amount := 670
AMEND   T121 | amount := 408
AMEND   T340 | amount := 792
VOID    T147
VOID    T223
AMEND   T160 | amount := 363
VOID    T139
AMEND   T346 | amount := 644
VOID    T256
AMEND   T237 | amount := 413
AMEND   T121 | amount := 480
VOID    T247
RESTORE T362
AMEND   T130 | amount := 527
VOID    T104
VOID    T385
AMEND   T168 | amount := 133
VOID    T208
AMEND   T335 | amount := 392
VOID    T374
RESTORE T256
VOID    T298
AMEND   T247 | amount := 51
AMEND   T354 | amount := 332
AMEND   T149 | amount := 835
AMEND   T227 | amount := 468
--- END LOG ---
