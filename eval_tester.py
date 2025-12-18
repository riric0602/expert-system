from execution.exec import Engine
from parsing.file_utils import parser
import os


tests = {
    # And conclusions
    "tester/inputs/eval_tests/and_conclusions/1.txt": {
        "A": True,
        "F": True,
        "K": True,
        "P": True
    },
    "tester/inputs/eval_tests/and_conclusions/2.txt": {
        "A": True,
        "F": True,
        "K": False,
        "P": True
    },
    # Or conditions
    "tester/inputs/eval_tests/or_conditions/3.txt": {
        "A": False
    },
    "tester/inputs/eval_tests/or_conditions/4.txt": {
        "A": True
    },
    "tester/inputs/eval_tests/or_conditions/5.txt": {
        "A": True
    },
    "tester/inputs/eval_tests/or_conditions/6.txt": {
        "A": True
    },
    # Xor conditions
    "tester/inputs/eval_tests/xor_conditions/7.txt": {
        "A": False
    },
    "tester/inputs/eval_tests/xor_conditions/8.txt": {
        "A": True
    },
    "tester/inputs/eval_tests/xor_conditions/9.txt": {
        "A": True
    },
    "tester/inputs/eval_tests/xor_conditions/10.txt": {
        "A": False
    },
    # Negation
    "tester/inputs/eval_tests/negation/12.txt": {
        "A": False
    },
    "tester/inputs/eval_tests/negation/13.txt": {
        "A": True
    },
    "tester/inputs/eval_tests/negation/14.txt": {
        "A": False
    },
    "tester/inputs/eval_tests/negation/15.txt": {
        "A": False
    },
    # Same conclusion
    "tester/inputs/eval_tests/same_conclusion/16.txt": {
        "A": False
    },
    "tester/inputs/eval_tests/same_conclusion/17.txt": {
        "A": True
    },
    "tester/inputs/eval_tests/same_conclusion/18.txt": {
        "A": True
    },
    "tester/inputs/eval_tests/same_conclusion/19.txt": {
        "A": True
    },
    # Parentheses
    "tester/inputs/eval_tests/parentheses/20.txt": {
        "E": False
    },
    "tester/inputs/eval_tests/parentheses/21.txt": {
        "E": True
    },
    "tester/inputs/eval_tests/parentheses/22.txt": {
        "E": False
    },
    "tester/inputs/eval_tests/parentheses/23.txt": {
        "E": False
    },
    "tester/inputs/eval_tests/parentheses/24.txt": {
        "E": True
    },
    "tester/inputs/eval_tests/parentheses/25.txt": {
        "E": True
    },
    "tester/inputs/eval_tests/parentheses/26.txt": {
        "E": False
    },
    "tester/inputs/eval_tests/parentheses/27.txt": {
        "E": False
    },
    "tester/inputs/eval_tests/parentheses/28.txt": {
        "E": False
    },
    "tester/inputs/eval_tests/parentheses/29.txt": {
        "E": True
    },
    "tester/inputs/eval_tests/parentheses/30.txt": {
        "E": True
    }
}


class Colors:
    BLUE = "\033[94m"   # Passed
    RED = "\033[91m"    # Failed
    YELLOW = "\033[93m" # Warnings
    CYAN = "\033[96m"   # Info
    END = "\033[0m"
    BOLD = "\033[1m"


def run_test(file_path, expected):
    pr = parser(file_path)
    engine = Engine(pr)
    results = engine.backward_chaining()
    
    output = {q.name: q.value for q in results}
    passed = all(output.get(k) == v for k, v in expected.items())
    
    return {
        "file": file_path,
        "passed": passed,
        "results": output,
        "expected": expected
    }

def print_summary(summary):
    total = len(summary)
    passed_count = sum(1 for r in summary if r['passed'])
    failed_count = total - passed_count
    percent_passed = (passed_count / total * 100) if total else 0

    print(f"\n{Colors.BOLD}{Colors.CYAN}==================== TEST SUMMARY ===================={Colors.END}")
    print(f"Total tests: {total} | Passed: {Colors.BLUE}{passed_count} ✅{Colors.END} | "
          f"Failed: {Colors.RED}{failed_count} ❌{Colors.END} | Success Rate: {percent_passed:.1f}%\n")

    for r in summary:
        status = f"{Colors.BLUE}PASSED ✅{Colors.END}" if r['passed'] else f"{Colors.RED}FAILED ❌{Colors.END}"
        print(f"{Colors.BOLD}Test:{Colors.END} {r['file']} | Status: {status}")

        if not r['passed']:
            print(f"  {Colors.YELLOW}Mismatched Results:{Colors.END}")
            for k, val in r['results'].items():
                expected_val = r['expected'].get(k)
                if expected_val is not None and val != expected_val:
                    print(f"    {k:<20}: got {val}, expected {expected_val}")
        else:
            # Optional: show results for passed tests
            print(f"  {Colors.CYAN}Results:{Colors.END}")
            for k, val in r['results'].items():
                print(f"    {k:<20}: {val}")

        print("-----------------------------------------------------")

    if failed_count > 0:
        print(f"\n{Colors.RED}{Colors.BOLD}Failed Tests:{Colors.END}")
        for r in summary:
            if not r['passed']:
                print(f" - {r['file']}")
    else:
        print(f"\n{Colors.BLUE}{Colors.BOLD}All tests passed! 🎉{Colors.END}")


if __name__ == "__main__":
    summary = []

    # Run tests
    for file_path, expected in tests.items():
        if os.path.exists(file_path):
            print(f"{Colors.CYAN}Running test: {file_path}{Colors.END}")
            result = run_test(file_path, expected)
            summary.append(result)
        else:
            print(f"{Colors.YELLOW}⚠️ File not found: {file_path}{Colors.END}")

    print_summary(summary)