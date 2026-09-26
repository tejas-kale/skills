---
name: german-shopping-receipts
description: Query the german_shopping_receipts BigQuery table with bq. Use when the user asks about groceries, supermarket spend, item prices, or that table.
---

# German Shopping Receipts

Answer grocery questions from `august-cirrus-399913.economics.german_shopping_receipts` using `bq`.

## Process

1. Translate the question into one Standard SQL query.
2. Run `bq query --nouse_legacy_sql --format=pretty '<sql>'`.
3. Summarise the answer, naming the filters, grouping, and date range it rests on.

Done when the query ran without error and the summary states every filter, grouping, and date bound that shaped the number.

## Schema

Reference the table path directly in `FROM` — no backticks, no escaping.

| Column | Type | Notes |
|---|---|---|
| supermarket | STRING | |
| date | DATE | Purchase date — the one to filter and group on |
| item_name_german | STRING | |
| item_name_english | STRING | |
| price | FLOAT | Per-item price; the column for item-level analysis |
| total_price | FLOAT | Receipt total, repeated on every line item — summing it multiplies by line count |
| inserted_at | TIMESTAMP | Load time, not purchase time |

A receipt is the set of rows sharing a `supermarket` and `date`. Count receipts with `COUNT(DISTINCT ...)` over that pair, and take a receipt total with `MAX(total_price)` per group.
