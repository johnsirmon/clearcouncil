#!/bin/bash
source clearcouncil_env/bin/activate
echo "🔍 Testing with last 7 days of data..."
python clearcouncil.py update-documents york_county_sc "last 7 days"
python clearcouncil.py analyze-voting york_county_sc "District 2" "last 7 days" --create-charts
echo "✅ Test completed! Check data/results/ for output"
