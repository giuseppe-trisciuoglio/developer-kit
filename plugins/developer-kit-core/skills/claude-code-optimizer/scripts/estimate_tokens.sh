#!/bin/bash
# Usage: ./estimate_tokens.sh [file_path]
# Default file: CLAUDE.md

FILE=${1:-CLAUDE.md}

if [ ! -f "$FILE" ]; then
    echo "Error: $FILE not found."
    exit 1
fi

TOTAL_TOKENS=$(wc -w < "$FILE" | awk '{print int($1 * 0.75)}')
FIRST_200_LINES_TOKENS=$(head -n 200 "$FILE" | wc -w | awk '{print int($1 * 0.75)}')

echo "--- Token Estimation for $FILE ---"
echo "Total estimated tokens: $TOTAL_TOKENS"
echo "First 200 lines estimated tokens: $FIRST_200_LINES_TOKENS"
echo "Target for first 200 lines: < 1,000 tokens"

if [ "$FIRST_200_LINES_TOKENS" -lt 1000 ]; then
    echo "✅ Optimization target met!"
else
    echo "❌ Optimization target exceeded. Consider moving detailed sections to separate files."
fi
