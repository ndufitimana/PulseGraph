# PulseGraph Usage Guide

## Quick Start: Making Your First Query

### Problem: Why Am I Getting Empty Results?

If you're getting responses like this:
```json
{
  "claims_a": [],
  "claims_b": [],
  "sentiment": {"delta": null, "note": "Missing signal for one or both periods."}
}
```

**This means:** The database doesn't have data for the periods you're querying.

---

## Solution: Seed the Database First

### Step 1: Run the Expanded Seed Script

```bash
# From project root
python3 scripts/seed_expanded.py
```

This will populate the database with:
- **Company:** NVIDIA (NVDA)
- **Periods:** Q1-2026, Q4-2025, Q3-2025
- **Data:** Revenue claims, sentiment signals, market reactions

**Output:**
```
Seeding Q1-2026 data...
Seeding Q4-2025 data...
Seeding Q3-2025 data...

✅ Seed complete!
   Company: NVIDIA (NVDA)
   Periods: Q1-2026, Q4-2025, Q3-2025
   Claims: 8 total
   Signals: 3 sentiment scores
```

---

## Step 2: Ask Questions That Match the Data

### Example 1: Your Original Question (Now Fixed!)

**Question:** "How did NVIDIA perform in Q4 2025 vs Q3 2025?"

**Request:**
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How did NVIDIA perform in Q4 2025 vs Q3 2025?",
    "period_a": "Q4-2025",
    "period_b": "Q3-2025"
  }'
```

**Expected Response:**
```json
{
  "company": {"name": "NVIDIA", "ticker": "NVDA"},
  "period_a": "Q4-2025",
  "period_b": "Q3-2025",
  "sentiment": {
    "delta": 0.04,
    "a": {"score": 0.72, "volume": 2100},
    "b": {"score": 0.68, "volume": 1800}
  },
  "claims_a": [
    {"text": "Q4 2025 revenue was $30.5 billion, beating analyst estimates.", "confidence": 0.90},
    {"text": "Data center revenue reached $25 billion driven by AI infrastructure.", "confidence": 0.87},
    ...
  ],
  "claims_b": [
    {"text": "Q3 2025 revenue was $28 billion with strong AI growth.", "confidence": 0.89},
    ...
  ]
}
```

### Example 2: Most Recent Quarter

**Question:** "How did NVIDIA perform in Q1 2026 vs Q4 2025?"

**Request:**
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How did NVIDIA do recently?",
    "company": "NVIDIA",
    "period_a": "Q1-2026",
    "period_b": "Q4-2025"
  }'
```

**Expected Response:**
```json
{
  "sentiment": {
    "delta": 0.06,
    "a": {"score": 0.78, "volume": 2500},
    "b": {"score": 0.72, "volume": 2100}
  },
  "claims_a": [
    {"text": "Q1 2026 revenue reached $35 billion, up 15% from Q4 2025.", "confidence": 0.92},
    {"text": "AI data center revenue grew 25% quarter-over-quarter.", "confidence": 0.88},
    ...
  ]
}
```

### Example 3: Use Auto-Detection (Let API Pick Periods)

**Request:**
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How is NVIDIA doing?",
    "company": "NVIDIA"
  }'
```

This will auto-select:
- `period_a`: Q1-2026 (current quarter based on today's date: Jan 18, 2026)
- `period_b`: Q4-2025 (previous quarter)

---

## Understanding Period Selection

### Automatic (No periods specified)

The API automatically calculates periods based on **current date**:

| Current Date | period_a (Latest) | period_b (Comparison) |
|--------------|-------------------|-----------------------|
| Jan 18, 2026 | Q1-2026 | Q4-2025 |
| Apr 15, 2026 | Q2-2026 | Q1-2026 |
| Jul 20, 2026 | Q3-2026 | Q2-2026 |
| Nov 10, 2026 | Q4-2026 | Q3-2026 |

### Manual (Specify periods explicitly)

Always specify both periods if you want specific quarters:

```json
{
  "question": "...",
  "period_a": "Q4-2025",
  "period_b": "Q3-2025"
}
```

---

## Common Mistakes & Solutions

### Mistake 1: Asking About Future Periods

❌ **Wrong:**
```json
{"question": "How will NVIDIA perform in Q3 2026?"}
```

✅ **Right:**
```json
{
  "question": "How did NVIDIA perform in Q3 2025?",
  "period_a": "Q3-2025",
  "period_b": "Q2-2025"
}
```

### Mistake 2: Not Seeding Data First

❌ **Wrong:** Query immediately after starting the API

✅ **Right:**
1. Run `python3 scripts/seed_expanded.py`
2. Then make queries

### Mistake 3: Asking About Unseeded Companies

❌ **Wrong:**
```json
{"question": "How did Tesla perform?"}
```
*Result:* `404 Company not found in graph: Tesla`

✅ **Right:** Only query companies that have been seeded (currently only NVIDIA)

Or add Tesla to the seed script first.

---

## Adding More Companies

To add Tesla, Microsoft, etc., create your own seed script or extend `seed_expanded.py`:

```python
# Add Tesla
tesla_id = upsert_company(driver, "Tesla", "TSLA")
tesla_ev = upsert_event(driver, tesla_id, period="Q4-2025", ...)

# Add claims and signals for Tesla...
```

---

## API Features

### Check Available Event & Signal Types

```bash
# List all event types
curl http://localhost:8000/event-types

# List all signal types
curl http://localhost:8000/signal-types
```

### Use Different Signal Types

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How volatile was NVIDIA stock?",
    "company": "NVIDIA",
    "signal_type": "volatility",
    "period_a": "Q4-2025",
    "period_b": "Q3-2025"
  }'
```

### Use Different Event Types

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How was the product launch received?",
    "company": "NVIDIA",
    "event_type": "product_launch",
    "period_a": "Q4-2025",
    "period_b": "Q3-2025"
  }'
```

---

## Troubleshooting

### Empty Results Even After Seeding

**Check:**
1. Did the seed script complete successfully?
2. Are you using the correct period format? (e.g., "Q3-2025" not "2025-Q3")
3. Are you querying the right company name? (case-sensitive)

**Debug:**
```bash
# Check what's in the database
curl http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "test",
    "company": "NVIDIA",
    "period_a": "Q3-2025",
    "period_b": "Q2-2025"
  }'
```

### "Company not found in graph"

**Solution:** The company hasn't been seeded yet. Run:
```bash
python3 scripts/seed_expanded.py
```

### "Invalid event type" or "Invalid signal type"

**Solution:** Check valid types:
```bash
curl http://localhost:8000/event-types
curl http://localhost:8000/signal-types
```

---

## Best Practices

### 1. Always Seed Data First
Before querying, make sure you've run a seed script.

### 2. Be Explicit with Periods
For predictable results, always specify both `period_a` and `period_b`.

### 3. Match Your Question to Seeded Data
Don't ask about Q4 2025 if you only seeded Q3 2025.

### 4. Use Company Name Exactly
The LLM entity extraction helps, but being explicit is better:
```json
{"company": "NVIDIA"}  // ✓ Clear and explicit
```

### 5. Check Available Data
Use the `/event-types` and `/signal-types` endpoints to see what's supported.

---

## Summary: Quick Command Reference

```bash
# 1. Seed the database
python3 scripts/seed_expanded.py

# 2. Check available types
curl http://localhost:8000/event-types
curl http://localhost:8000/signal-types

# 3. Query with explicit periods (recommended)
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How did NVIDIA perform in Q4 2025 vs Q3 2025?",
    "company": "NVIDIA",
    "period_a": "Q4-2025",
    "period_b": "Q3-2025"
  }'

# 4. Let API auto-calculate periods
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How is NVIDIA doing?",
    "company": "NVIDIA"
  }'
```

---

## Next Steps

1. **Run the seed script:** `python3 scripts/seed_expanded.py`
2. **Try the examples above**
3. **Add more companies and periods as needed**
4. **Explore different signal types (volatility, volume, etc.)**
5. **Try different event types (product_launch, acquisition, etc.)**

Happy querying! 🚀
