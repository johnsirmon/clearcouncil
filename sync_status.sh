#!/bin/bash
echo "📊 ClearCouncil Sync Status"
echo "=========================="
echo ""

if [[ -f "data/sync.log" ]]; then
    echo "📋 Last Sync:"
    tail -5 data/sync.log
    echo ""
fi

echo "📁 Data Directory Status:"
echo "  PDFs: $(find data/PDFs -name "*.pdf" 2>/dev/null | wc -l) files"
echo "  Results: $(find data/results -name "*.csv" 2>/dev/null | wc -l) CSV files"
echo "  Charts: $(find data/results -name "*.png" -o -name "*.html" 2>/dev/null | wc -l) charts"
echo ""

if [[ -f "data/results/sync_summary.txt" ]]; then
    echo "📈 Last Summary:"
    cat data/results/sync_summary.txt
fi
