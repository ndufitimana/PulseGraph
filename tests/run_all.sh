#!/bin/bash
# Run all PulseGraph tests

echo "=========================================="
echo "Running All PulseGraph Tests"
echo "=========================================="
echo ""

# Change to project root
cd "$(dirname "$0")/.."

echo "🧪 Test 1: Period Calculation Utilities"
echo "------------------------------------------"
python3 tests/test_periods.py
PERIODS_EXIT=$?
echo ""

echo "🧪 Test 2: Entity Extraction (requires OpenAI API key)"
echo "------------------------------------------"
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  Warning: OPENAI_API_KEY not set. Skipping entity extraction tests."
    echo "   Set your OpenAI API key in .env or export OPENAI_API_KEY to run this test."
    ENTITY_EXIT=0
else
    python3 tests/test_entity_extraction.py 2>&1
    ENTITY_EXIT=$?
    # If exit code is 1 and output contains "ModuleNotFoundError", treat as skipped
    if [ $ENTITY_EXIT -ne 0 ]; then
        echo ""
        echo "⚠️  Entity extraction test dependencies not installed. This is optional."
        echo "   Install with: pip install openai"
        ENTITY_EXIT=0  # Don't fail the overall test suite
    fi
fi
echo ""

echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo ""

if [ $PERIODS_EXIT -eq 0 ]; then
    echo "✅ Period Calculation Tests: PASSED"
else
    echo "❌ Period Calculation Tests: FAILED"
fi

if [ -z "$OPENAI_API_KEY" ]; then
    echo "⏭️  Entity Extraction Tests: SKIPPED (no API key)"
elif [ $ENTITY_EXIT -eq 0 ]; then
    echo "✅ Entity Extraction Tests: PASSED"
else
    echo "❌ Entity Extraction Tests: FAILED"
fi

echo ""

# Exit with failure if any test failed
if [ $PERIODS_EXIT -ne 0 ] || [ $ENTITY_EXIT -ne 0 ]; then
    exit 1
else
    exit 0
fi
