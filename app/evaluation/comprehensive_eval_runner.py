"""Comprehensive Evaluation Runner with Detailed Reports"""
import os
import sys
import json
import time
import asyncio
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.evaluation.test_cases import TestCaseLibrary
from app.evaluation.agent_evaluator import AgentEvaluator


class ComprehensiveEvaluationRunner:
    """Runs comprehensive evaluation with detailed reporting"""

    def __init__(self, api_key: str, output_dir: str = "./evaluation_results"):
        self.api_key = api_key
        self.evaluator = AgentEvaluator(api_key)
        self.output_dir = output_dir
        Path(output_dir).mkdir(parents=True, exist_ok=True)

    async def run_all_tests(self, test_ids: List[str] = None) -> Dict[str, Any]:
        """Run all or specified tests"""

        print("=" * 70)
        print("COMPREHENSIVE AGENT EVALUATION")
        print("=" * 70)

        test_cases = TestCaseLibrary.get_all_test_cases()

        if test_ids:
            test_cases = [tc for tc in test_cases if tc["id"] in test_ids]

        print(f"\nRunning {len(test_cases)} test cases...\n")

        results = {
            "evaluation_run": {
                "timestamp": datetime.now().isoformat(),
                "total_tests": len(test_cases),
                "gemini_model": "gemini-2.5-flash"
            },
            "test_results": [],
            "summary": {}
        }

        # Run each test case
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{'='*70}")
            print(f"Test {i}/{len(test_cases)}: {test_case['id']}")
            print(f"Business: {test_case['profile'].business_name}")
            print(f"Category: {test_case['category']}")
            print(f"{'='*70}")

            try:
                test_result = await self.evaluator.run_full_evaluation(test_case)
                results["test_results"].append(test_result)

                # Print summary
                print(f"\n✓ Test completed in {test_result['total_duration']:.2f}s")
                print(f"  Average Agent Score: {test_result['average_agent_score']:.2f}")
                print(f"  Critic Overall Score: {test_result['critic_overall_score']:.2f}")
                print(f"  Meets Min Score: {'✓' if test_result['meets_minimum_score'] else '✗'}")

                # Agent breakdown
                print(f"\n  Agent Scores:")
                for agent_name, agent_result in test_result["agents"].items():
                    status = "✓" if agent_result.get("success", False) else "✗"
                    score = agent_result.get("score", 0)
                    duration = agent_result.get("duration_seconds", 0)
                    print(f"    {status} {agent_name.capitalize()}: {score:.2f} ({duration:.2f}s)")

            except Exception as e:
                print(f"\n✗ Test failed: {str(e)}")
                import traceback
                traceback.print_exc()

                results["test_results"].append({
                    "test_id": test_case["id"],
                    "business_name": test_case["profile"].business_name,
                    "category": test_case["category"],
                    "overall_success": False,
                    "error": str(e)
                })

        # Generate summary
        results["summary"] = self._generate_summary(results["test_results"])

        # Print final summary
        self._print_summary(results["summary"])

        # Save results
        self._save_results(results)

        return results

    def _generate_summary(self, test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive summary statistics"""

        summary = {
            "total_tests": len(test_results),
            "successful_tests": 0,
            "failed_tests": 0,
            "average_duration": 0,
            "average_agent_score": 0,
            "average_critic_score": 0,
            "tests_meeting_min_score": 0,
            "agent_performance": {},
            "category_performance": {},
            "duration_stats": {
                "min": float('inf'),
                "max": 0,
                "total": 0
            }
        }

        successful_tests = [t for t in test_results if t.get("overall_success", False)]
        summary["successful_tests"] = len(successful_tests)
        summary["failed_tests"] = summary["total_tests"] - summary["successful_tests"]

        if not successful_tests:
            return summary

        # Calculate averages
        durations = [t["total_duration"] for t in successful_tests]
        summary["average_duration"] = round(sum(durations) / len(durations), 2)
        summary["duration_stats"]["min"] = round(min(durations), 2)
        summary["duration_stats"]["max"] = round(max(durations), 2)
        summary["duration_stats"]["total"] = round(sum(durations), 2)

        agent_scores = [t["average_agent_score"] for t in successful_tests]
        summary["average_agent_score"] = round(sum(agent_scores) / len(agent_scores), 2)

        critic_scores = [t["critic_overall_score"] for t in successful_tests]
        summary["average_critic_score"] = round(sum(critic_scores) / len(critic_scores), 2)

        summary["tests_meeting_min_score"] = sum(
            1 for t in successful_tests if t.get("meets_minimum_score", False)
        )

        # Agent-specific performance
        agent_names = ["persona", "competitor", "planner", "creative", "performance", "critic"]
        for agent_name in agent_names:
            agent_scores = []
            agent_durations = []
            for test in successful_tests:
                agent_result = test["agents"].get(agent_name, {})
                if agent_result.get("success", False):
                    agent_scores.append(agent_result.get("score", 0))
                    agent_durations.append(agent_result.get("duration_seconds", 0))

            if agent_scores:
                summary["agent_performance"][agent_name] = {
                    "average_score": round(sum(agent_scores) / len(agent_scores), 2),
                    "average_duration": round(sum(agent_durations) / len(agent_durations), 2),
                    "success_rate": len(agent_scores) / len(successful_tests)
                }

        # Category performance
        categories = {}
        for test in successful_tests:
            category = test["category"]
            if category not in categories:
                categories[category] = {
                    "count": 0,
                    "scores": [],
                    "critic_scores": []
                }
            categories[category]["count"] += 1
            categories[category]["scores"].append(test["average_agent_score"])
            categories[category]["critic_scores"].append(test["critic_overall_score"])

        for category, data in categories.items():
            summary["category_performance"][category] = {
                "test_count": data["count"],
                "avg_score": round(sum(data["scores"]) / len(data["scores"]), 2),
                "avg_critic_score": round(sum(data["critic_scores"]) / len(data["critic_scores"]), 2)
            }

        return summary

    def _print_summary(self, summary: Dict[str, Any]):
        """Print formatted summary"""

        print("\n" + "=" * 70)
        print("EVALUATION SUMMARY")
        print("=" * 70)

        print(f"\nOverall Results:")
        print(f"  Total Tests: {summary['total_tests']}")
        print(f"  Successful: {summary['successful_tests']} ✓")
        print(f"  Failed: {summary['failed_tests']} ✗")
        print(f"  Success Rate: {summary['successful_tests']/summary['total_tests']*100:.1f}%")

        if summary["successful_tests"] > 0:
            print(f"\nPerformance Metrics:")
            print(f"  Average Agent Score: {summary['average_agent_score']:.2f}")
            print(f"  Average Critic Score: {summary['average_critic_score']:.2f}")
            print(f"  Tests Meeting Min Score: {summary['tests_meeting_min_score']}/{summary['successful_tests']}")

            print(f"\nDuration Statistics:")
            print(f"  Average: {summary['average_duration']:.2f}s")
            print(f"  Min: {summary['duration_stats']['min']:.2f}s")
            print(f"  Max: {summary['duration_stats']['max']:.2f}s")
            print(f"  Total: {summary['duration_stats']['total']:.2f}s")

            print(f"\nAgent Performance:")
            for agent_name, perf in summary["agent_performance"].items():
                print(f"  {agent_name.capitalize()}:")
                print(f"    Score: {perf['average_score']:.2f}")
                print(f"    Duration: {perf['average_duration']:.2f}s")
                print(f"    Success Rate: {perf['success_rate']*100:.1f}%")

            print(f"\nCategory Performance:")
            for category, perf in summary["category_performance"].items():
                print(f"  {category}:")
                print(f"    Tests: {perf['test_count']}")
                print(f"    Avg Score: {perf['avg_score']:.2f}")
                print(f"    Avg Critic Score: {perf['avg_critic_score']:.2f}")

        print("\n" + "=" * 70)

    def _save_results(self, results: Dict[str, Any]):
        """Save results to JSON file"""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"evaluation_results_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        print(f"\n📊 Results saved to: {filepath}")

        # Also save a summary-only file
        summary_filename = f"evaluation_summary_{timestamp}.json"
        summary_filepath = os.path.join(self.output_dir, summary_filename)

        with open(summary_filepath, 'w') as f:
            json.dump({
                "timestamp": results["evaluation_run"]["timestamp"],
                "summary": results["summary"]
            }, f, indent=2)

        print(f"📊 Summary saved to: {summary_filepath}")


def main():
    """Main execution"""

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set")
        sys.exit(1)

    runner = ComprehensiveEvaluationRunner(api_key)

    # Option to run specific tests or all
    import argparse
    parser = argparse.ArgumentParser(description="Run comprehensive agent evaluation")
    parser.add_argument(
        "--tests",
        nargs="+",
        help="Specific test IDs to run (e.g., test_001 test_002)"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run quick evaluation (first 5 tests only)"
    )

    args = parser.parse_args()

    if args.quick:
        test_ids = [f"test_{i:03d}" for i in range(1, 6)]
        results = asyncio.run(runner.run_all_tests(test_ids))
    elif args.tests:
        results = asyncio.run(runner.run_all_tests(args.tests))
    else:
        results = asyncio.run(runner.run_all_tests())

    # Exit with appropriate code
    sys.exit(0 if results["summary"]["failed_tests"] == 0 else 1)


if __name__ == "__main__":
    main()
