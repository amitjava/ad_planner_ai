#!/bin/bash

echo "Testing strengths field in critic evaluation..."

RESPONSE=$(curl -s -X POST http://127.0.0.1:8000/plan \
  -H "Content-Type: application/json" \
  -d '{
    "profile": {
      "business_name": "Test Coffee Shop",
      "business_type": "Coffee Shop",
      "location": "San Francisco",
      "zip_code": "94107",
      "miles_radius": 3,
      "goal": "Increase lunchtime traffic",
      "monthly_budget": 2500,
      "duration_weeks": 10,
      "competitors": ["Starbucks"],
      "is_local": true
    }
  }')

echo "$RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print('✓ Plan generated successfully')
print('✓ Strengths field present:', 'strengths' in data.get('critic_evaluation', {}))
strengths = data.get('critic_evaluation', {}).get('strengths', [])
print('✓ Number of strengths:', len(strengths))
if strengths:
    print('\nStrengths:')
    for i, s in enumerate(strengths, 1):
        print(f'{i}. {s}')
else:
    print('\n⚠ No strengths found in response')
    print('Critic evaluation keys:', list(data.get('critic_evaluation', {}).keys()))
"
