import os
import sys
import json
from dotenv import load_dotenv

# Setup Python Path to import from directories
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(base_dir, "agent-1-sentry"))
sys.path.append(os.path.join(base_dir, "agent-2-engineer"))
sys.path.append(base_dir)

load_dotenv(dotenv_path=os.path.join(base_dir, ".env"))

from sentry_parser import SentryParser
from engineer_agent import build_prompt, call_featherless, build_refactor_prompt
from reviewer_agent import run_code_evaluation

def run_e2e_test():
    print("=" * 60)
    print("🔬 End-to-End Log Diagnostics & Review Pipeline")
    print("=" * 60)

    # 1. Simulate a crash log
    crash_log = """
    2026-06-19 14:00:00 [ERROR] Calculation failed:
    Traceback (most recent call last):
      File "/app/analytics.py", line 55, in calculate_average
        result = total / count
    ZeroDivisionError: division by zero
    """
    
    print("\n[Step 1] Initializing Sentry Parser (Agent 1)...")
    parser = SentryParser()
    report = parser.parse_log(crash_log)
    report_dict = report.model_dump()
    print("✅ Structured error report generated:")
    print(json.dumps(report_dict, indent=2))

    # 2. Generate Initial Patch (Agent 2)
    print("\n[Step 2] Formulating initial patch with Agent 2 (Mistral via Featherless)...")
    prompt = build_prompt(report_dict)
    initial_patch = call_featherless(prompt)
    print("💻 Initial Patch:")
    print("-" * 40)
    print(initial_patch)
    print("-" * 40)

    # 3. Simulate Reviewer (Agent 3)
    print("\n[Step 3] Running Code Evaluation with Agent 3 (Llama 3.3 via CrewAI)...")
    evaluation_report = str(run_code_evaluation(initial_patch))
    print("📝 Reviewer Evaluation Report:")
    print("-" * 40)
    print(evaluation_report)
    print("-" * 40)

    # 4. Check for rejection and trigger refactor if needed
    if "REJECTED" in evaluation_report:
        print("\n❌ Initial patch was REJECTED. Triggering Refactor Loop...")
        refactor_prompt = build_refactor_prompt(report_dict, initial_patch, evaluation_report)
        print("\n[Step 4] Calling Agent 2 to refactor code based on critique...")
        refactored_patch = call_featherless(refactor_prompt)
        print("💻 Refactored Patch:")
        print("-" * 40)
        print(refactored_patch)
        print("-" * 40)

        print("\n[Step 5] Running Code Evaluation on Refactored Patch...")
        final_report = str(run_code_evaluation(refactored_patch))
        print("📝 Final Reviewer Evaluation Report:")
        print("-" * 40)
        print(final_report)
        print("-" * 40)
        
        if "APPROVED" in final_report:
            print("\n🎉 Success! E2E feedback loop completed. Refactored patch is APPROVED.")
        else:
            print("\n⚠️ E2E loop completed. Refactored patch is still REJECTED.")
    else:
        print("\n🎉 E2E loop completed. Initial patch was APPROVED immediately.")

def run_targeted_refactor_test():
    print("\n" + "=" * 60)
    print("🎯 Targeted Refactoring Test (Forcing Rejection and Repair)")
    print("=" * 60)

    # Mock error report
    mock_report = {
        "error_type": "ZeroDivisionError",
        "error_message": "division by zero",
        "file_path": "api/analytics.py",
        "line_number": 55,
        "language": "Python",
        "stack_trace": "ZeroDivisionError: division by zero"
    }

    # Mock a faulty patch
    faulty_patch = """def calculate_average(total, count):
    # Simply divide total by count
    return total / count
"""

    # Mock reviewer critique
    critique = "REJECTED: The code contains a critical bug. It does not handle the case where 'count' is 0 or None, which will raise a ZeroDivisionError or TypeError. Add parameter validation to check if count is zero or falsey, and return 0.0 or handle it gracefully."

    print("\n[Targeted Step 1] Creating refactoring prompt using previous patch and critique...")
    refactor_prompt = build_refactor_prompt(mock_report, faulty_patch, critique)
    
    print("\n[Targeted Step 2] Invoking Agent 2 (Mistral via Featherless) for refactored patch...")
    refactored_patch = call_featherless(refactor_prompt)
    print("💻 Refactored Patch:")
    print("-" * 40)
    print(refactored_patch)
    print("-" * 40)

    print("\n[Targeted Step 3] Evaluating refactored patch with Agent 3...")
    evaluation_report = str(run_code_evaluation(refactored_patch))
    print("📝 Reviewer Evaluation Report:")
    print("-" * 40)
    print(evaluation_report)
    print("-" * 40)

    if "APPROVED" in evaluation_report:
        print("\n🎉 Success! Targeted refactor test passed. Patch corrected and APPROVED.")
    else:
        print("\n⚠️ Targeted refactor completed, but final report status is not APPROVED.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--e2e", action="store_true", help="Run the full E2E pipeline test")
    parser.add_argument("--refactor", action="store_true", help="Run targeted refactor test")
    args = parser.parse_args()

    # Default to running both if no specific flag is provided
    if not args.e2e and not args.refactor:
        run_targeted_refactor_test()
        run_e2e_test()
    else:
        if args.refactor:
            run_targeted_refactor_test()
        if args.e2e:
            run_e2e_test()
