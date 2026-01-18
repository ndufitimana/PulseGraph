# Dynamic Period Calculation

## Overview

The hardcoded periods (`Q3-2025`, `Q2-2025`) have been replaced with a dynamic period calculation system. The API now automatically calculates the current quarter and comparison periods based on the system date.

## What Changed

### Before (Hardcoded)
```python
class AskRequest(BaseModel):
    period_a: str = Field("Q3-2025", description="Latest period (MVP default)")
    period_b: str = Field("Q2-2025", description="Comparison period (MVP default)")
```

**Problems:**
- Hardcoded to Q3-2025 and Q2-2025
- Would become outdated over time
- Required manual updates each quarter
- Not flexible for different use cases

### After (Dynamic)
```python
class AskRequest(BaseModel):
    period_a: Optional[str] = Field(None, description="Latest period (defaults to current quarter if not provided)")
    period_b: Optional[str] = Field(None, description="Comparison period (defaults to previous quarter if not provided)")
```

**Benefits:**
- Automatically calculates current quarter from system date
- Always up-to-date without code changes
- Still allows manual override by providing explicit periods
- Flexible for historical comparisons

## Usage

### API Requests

#### Option 1: Use Dynamic Defaults (Recommended)
```bash
# No periods specified → automatically uses current and previous quarter
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How did NVIDIA perform?",
    "company": "NVIDIA"
  }'

# Response will use:
# - period_a: Q1-2026 (current quarter as of Jan 2026)
# - period_b: Q4-2025 (previous quarter)
```

#### Option 2: Specify Custom Periods
```bash
# Explicitly provide periods for historical analysis
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How did NVIDIA perform?",
    "company": "NVIDIA",
    "period_a": "Q3-2025",
    "period_b": "Q2-2025"
  }'
```

#### Option 3: Mix Dynamic and Custom
```bash
# Use current quarter for period_a, specify period_b
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How did NVIDIA perform?",
    "company": "NVIDIA",
    "period_b": "Q1-2025"
  }'

# period_a will be calculated automatically
# period_b will use Q1-2025
```

## Period Utilities Module

New module: `utils/periods.py`

### Key Functions

#### `get_default_periods()`
Get default periods for API requests (current and previous quarter).

```python
from utils.periods import get_default_periods

period_a, period_b = get_default_periods()
# Returns: ('Q1-2026', 'Q4-2025') as of Jan 2026
```

#### `get_current_quarter()`
Get the current fiscal quarter and year.

```python
from utils.periods import get_current_quarter

quarter, year = get_current_quarter()
# Returns: (1, 2026) for Q1-2026
```

#### `format_period()` and `parse_period()`
Convert between quarter numbers and period strings.

```python
from utils.periods import format_period, parse_period

# Format
period = format_period(3, 2025)
# Returns: 'Q3-2025'

# Parse
quarter, year = parse_period('Q3-2025')
# Returns: (3, 2025)
```

#### `get_period_offset()`
Calculate a period offset by N quarters.

```python
from utils.periods import get_period_offset

# Go back 2 quarters from Q3-2025
period = get_period_offset('Q3-2025', -2)
# Returns: 'Q1-2025'

# Go forward 2 quarters
period = get_period_offset('Q3-2025', 2)
# Returns: 'Q1-2026'
```

#### `validate_period()`
Validate period string format.

```python
from utils.periods import validate_period

validate_period('Q3-2025')  # True
validate_period('Q5-2025')  # False
validate_period('2025-Q3')  # False
```

### Full API

```python
from utils.periods import (
    get_current_quarter,      # Get current quarter and year
    get_previous_quarter,     # Get previous quarter
    get_next_quarter,         # Get next quarter
    format_period,            # Format quarter + year as string
    parse_period,             # Parse period string to quarter + year
    get_latest_period,        # Get current period as string
    get_comparison_period,    # Get N quarters back
    get_default_periods,      # Get (current, previous) tuple
    get_period_offset,        # Offset a period by N quarters
    validate_period,          # Validate period format
)
```

## Testing

Run the test suite to verify period calculations:

```bash
python3 tests/test_periods.py
```

This tests:
- Current quarter detection for various dates
- Quarter navigation (previous/next)
- Period parsing and formatting
- Default period calculation
- Period offset calculations
- Validation

## Implementation Details

### Quarter Calculation Logic

Standard calendar quarters:
- Q1: January - March (months 1-3)
- Q2: April - June (months 4-6)
- Q3: July - September (months 7-9)
- Q4: October - December (months 10-12)

### Automatic Updates

The system automatically:
1. Detects the current quarter from `datetime.now(timezone.utc)`
2. Calculates the previous quarter (handling year rollover)
3. Formats periods as "Q[1-4]-YYYY"
4. Falls back to user-provided periods if specified

### Backwards Compatibility

The API remains fully backwards compatible:
- Old requests with explicit periods still work
- New requests without periods get dynamic defaults
- Mixed approach (one dynamic, one explicit) is supported

## Migration Guide

### For API Users

No changes required! The API will automatically use dynamic periods if you don't specify them.

**Optional:** Remove hardcoded periods from your API calls to use dynamic defaults:

```diff
{
  "question": "How did NVIDIA perform?",
  "company": "NVIDIA",
-  "period_a": "Q3-2025",
-  "period_b": "Q2-2025"
}
```

### For Developers

If you're extending the codebase:

1. **Use the utilities:** Import from `utils.periods` instead of hardcoding periods
2. **Calculate dynamically:** Use `get_default_periods()` for defaults
3. **Validate input:** Use `validate_period()` to check user input
4. **Parse safely:** Use `parse_period()` with try/except for parsing

## Examples

### Current System Date: January 18, 2026

| Scenario | period_a | period_b | Result |
|----------|----------|----------|--------|
| No periods specified | `None` | `None` | Q1-2026, Q4-2025 |
| Only period_a | `"Q3-2025"` | `None` | Q3-2025, Q4-2025 |
| Only period_b | `None` | `"Q1-2025"` | Q1-2026, Q1-2025 |
| Both specified | `"Q3-2025"` | `"Q2-2025"` | Q3-2025, Q2-2025 |

### Comparison Lookback

```python
# Current quarter: Q1-2026
get_comparison_period(periods_back=1)  # Q4-2025
get_comparison_period(periods_back=2)  # Q3-2025
get_comparison_period(periods_back=4)  # Q1-2025 (1 year back)
get_comparison_period(periods_back=8)  # Q1-2024 (2 years back)
```

## Related Files

- `utils/periods.py` - Period calculation utilities
- `utils/__init__.py` - Package exports
- `api/main.py` - API implementation using dynamic periods
- `tests/test_periods.py` - Test suite
- `DYNAMIC_PERIODS.md` - This documentation

## Future Enhancements

Potential improvements:
- Support for fiscal year calendars (non-calendar quarters)
- Configurable quarter start months per company
- Period validation against available data in Neo4j
- Auto-suggest valid periods based on data availability
