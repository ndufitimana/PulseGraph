# PulseGraph Tests

This directory contains test scripts for the PulseGraph project.

## Test Files

### `test_entity_extraction.py`
Tests for LLM-based company entity extraction.

**What it tests:**
- Company name extraction from various question formats
- Ticker symbol extraction (NVDA, TSLA, etc.)
- Confidence scoring
- Handling ambiguous questions
- Edge cases (no company mentioned, multiple companies)

**Run:**
```bash
python3 tests/test_entity_extraction.py
```

**Requirements:**
- OpenAI API key in `.env` file
- `extract.llm_entity` module

---

### `test_periods.py`
Tests for dynamic period calculation utilities.

**What it tests:**
- Current quarter detection for various dates
- Quarter navigation (previous/next with year rollover)
- Period string parsing and formatting
- Default period calculation
- Period offset calculations (+/- N quarters)
- Format validation

**Run:**
```bash
python3 tests/test_periods.py
```

**Requirements:**
- `utils.periods` module
- No external dependencies (uses stdlib only)

---

### `test_query_generation.py`
Tests for LLM-based search query generation.

**What it tests:**
- Dynamic query generation for different companies/industries
- Event-specific query optimization (earnings, product launch, etc.)
- Source-type-specific queries (news, blog, forum, etc.)
- Multi-source query generation
- Comparison of hardcoded vs LLM-generated queries
- Alternative query suggestions

**Run:**
```bash
python3 tests/test_query_generation.py
```

**Requirements:**
- OpenAI API key in `.env` file
- `ingest.llm_query_gen` module

---

## Running All Tests

### Quick Start (Recommended)

Use the test runner script to run all tests:

```bash
./tests/run_all.sh
```

This will:
- Run all test files in sequence
- Skip entity extraction tests if no OpenAI API key is set
- Show a summary of results

### Individual Tests

To run tests individually:

```bash
# Run entity extraction tests
python3 tests/test_entity_extraction.py

# Run period calculation tests
python3 tests/test_periods.py
```

## Test Output

All tests include:
- ✓ Pass indicators
- ✗ Fail indicators
- Detailed output showing expected vs actual results
- Summary statistics

## Adding New Tests

When adding new test files:

1. Create test file in this directory: `tests/test_<feature>.py`
2. Add a docstring explaining what the test does
3. Include usage instructions in the docstring
4. Update this README with a new section
5. Follow the existing test structure:
   ```python
   #!/usr/bin/env python3
   """
   Test description here.

   Usage:
       python3 tests/test_<feature>.py
   """

   def test_something():
       print("=" * 80)
       print("Testing Something")
       print("=" * 80)
       # Test implementation

   if __name__ == "__main__":
       test_something()
   ```

## Notes

- These are **integration/functional tests**, not unit tests
- They test actual functionality with real dependencies
- Some tests may require API keys or external services
- Tests are designed to be run individually during development
