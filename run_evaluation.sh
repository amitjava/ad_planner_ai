#!/bin/bash
# Run Agent Evaluation

set -e

echo "🧪 Smart Ad Planner - Agent Evaluation"
echo "======================================"

# Load environment variables
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check for API key
if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ GEMINI_API_KEY not set"
    exit 1
fi

# Create results directory
mkdir -p evaluation_results

# Parse arguments
case "$1" in
    quick)
        echo "Running QUICK evaluation (5 tests)..."
        python3 -m app.evaluation.comprehensive_eval_runner --quick
        ;;
    specific)
        shift
        echo "Running SPECIFIC tests: $@"
        python3 -m app.evaluation.comprehensive_eval_runner --tests "$@"
        ;;
    *)
        echo "Running FULL evaluation (all 15 tests)..."
        echo "This may take 10-15 minutes..."
        echo ""
        python3 -m app.evaluation.comprehensive_eval_runner
        ;;
esac

echo ""
echo "✅ Evaluation complete!"
echo "📊 Results saved in ./evaluation_results/"
