from execution.exec import Engine, ContradictionException
from parsing.file_utils import parser
import os

tests = {
    # Unit tests
    "inputs/unit_tests/and_rules.txt": {
        "C": True,
        "D": True,
        "E": False,
        "F": False,
        "I": False,
        "J": False,
    },
    "inputs/unit_tests/or_rules.txt": {
        "C": True,
        "D": True,
        "E": False,
        "F": False,
        "I": True,
        "J": True,
        "K": True,
        "L": True
    },
    "inputs/unit_tests/xor_rules.txt": {
        "C": False,
        "D": False,
        "E": False,
        "F": False,
        "I": True,
        "J": True,
        "K": False,
        "L": False
    },
    "inputs/unit_tests/not_rules.txt": {
        "D": False,
        "E": False,
        "F": True,
        "X": True,
        "Y": False,
        "Z": True
    },
    # Complex tests
    # And in conclusions
    "inputs/complex_tests/and_conclusions/1.txt": {
        "A": True,
        "B": True,
        "C": True
    },
    "inputs/complex_tests/and_conclusions/2.txt": {
        "I": True,
        "J": True,
        "K": True,
        "M": False,
    },
    "inputs/complex_tests/and_conclusions/3.txt": {
        "N": False,
        "O": True,
        "P": False,
        "R": False,
    },
    # Negation
    "inputs/complex_tests/negation/1.txt": {
        "B": True,
        "C": True,
    },
    "inputs/complex_tests/negation/2.txt": {
        "B": False,
        "C": False,
    },
    "inputs/complex_tests/negation/3.txt": {
        "B": False,
        "C": False,
    },
    # Or conditions
    "inputs/complex_tests/or_conditions/1.txt": {
        "C": False,
    },
    "inputs/complex_tests/or_conditions/2.txt": {
        "E": False,
    },
    "inputs/complex_tests/or_conditions/3.txt": {
        "F": True,
    },
    "inputs/complex_tests/or_conditions/4.txt": {
        "C": True,
        "D": True,
        "F": False
    },
    # Parentheses
    "inputs/complex_tests/parentheses/1.txt": {
        "C": True,
        "E": False
    },
    "inputs/complex_tests/parentheses/2.txt": {
        "D": True,
        "E": False
    },
    "inputs/complex_tests/parentheses/3.txt": {
        "E": False,
        "H": True
    },
    "inputs/complex_tests/parentheses/4.txt": {
        "D": True,
        "F": True
    },
    "inputs/complex_tests/parentheses/5.txt": {
        "A": True,
        "B": False,
        "C": True
    },
    "inputs/complex_tests/parentheses/6.txt": {
        "B": True,
        "C": False,
        "E": False
    },
    # Same conclusion rules
    "inputs/complex_tests/same_conclusion/1.txt": {
        "B": False,
        "C": False
    },
    "inputs/complex_tests/same_conclusion/2.txt": {
        "C": True
    },
    "inputs/complex_tests/same_conclusion/3.txt": {
        "C": True,
        "F": True
    },
    # Xor conditions
    "inputs/complex_tests/xor_conditions/1.txt": {
        "C": False,
        "D": False
    },
    "inputs/complex_tests/xor_conditions/2.txt": {
        "C": True,
        "E": True
    },
    "inputs/complex_tests/xor_conditions/3.txt": {
        "C": True,
        "E": False
    },
    "inputs/complex_tests/xor_conditions/4.txt": {
        "B": True,
        "E": True,
        "G": False
    },
    # Or conclusions
    "inputs/complex_tests/or_conclusions/1.txt": {
        "C": None,
        "D": None
    },
    "inputs/complex_tests/or_conclusions/2.txt": {
        "C": False,
        "D": True,
    },
    "inputs/complex_tests/or_conclusions/3.txt": {
        "E": False,
        "D": False,
    },
    "inputs/complex_tests/or_conclusions/4.txt": {
        "E": False,
        "D": False,
        "I": None,
        "J": None,
        "C": True,
        "F": False
    },
    # Xor conclusions
    "inputs/complex_tests/xor_conclusions/1.txt": {
        "D": False,
        "E": True
    },
    "inputs/complex_tests/xor_conclusions/2.txt": {
        "E": True,
        "F": True
    },
    "inputs/complex_tests/xor_conclusions/3.txt": {
        "E": True,
        "E": True,
        "I": False
    },
    "inputs/complex_tests/xor_conclusions/4.txt": {
        "D": None,
        "E": None
    },
}

contradiction_tests = [
    "inputs/complex_tests/contradictions/1.txt",
    "inputs/complex_tests/contradictions/2.txt",
    "inputs/complex_tests/contradictions/3.txt",
    "inputs/complex_tests/contradictions/4.txt"
]


class Colors:
    GREEN = "\033[94m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
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


def run_contradiction_test(file_path):
    try:
        pr = parser(file_path)
        engine = Engine(pr)
        engine.backward_chaining()
        return {"file": file_path, "passed": False, "error": "No ContradictionException was raised"}
    except ContradictionException:
        return {"file": file_path, "passed": True}
    except Exception as e:
        return {"file": file_path, "passed": False, "error": f"Unexpected exception: {type(e).__name__}"}


def print_summary(summary):
    total = len(summary)
    passed_count = sum(1 for r in summary if r['passed'])
    failed_count = total - passed_count
    percent_passed = (passed_count / total * 100) if total else 0

    print(f"\n{Colors.BOLD}{Colors.CYAN}==================== TEST SUMMARY ===================={Colors.END}")
    print(f"Total tests: {total} | Passed: {Colors.GREEN}{passed_count} ✅{Colors.END} | "
          f"Failed: {Colors.RED}{failed_count} ❌{Colors.END} | Success Rate: {percent_passed:.1f}%\n")

    for r in summary:
        status = f"{Colors.GREEN}PASSED ✅{Colors.END}" if r['passed'] else f"{Colors.RED}FAILED ❌{Colors.END}"
        print(f"{Colors.BOLD}Test:{Colors.END} {r['file']} | Status: {status}")

        if not r['passed']:
            if 'results' in r and 'expected' in r:
                print(f"  {Colors.YELLOW}Mismatched Results:{Colors.END}")
                for k, val in r['results'].items():
                    expected_val = r['expected'].get(k)
                    if expected_val is not None and val != expected_val:
                        print(f"    {k:<20}: got {val}, expected {expected_val}")
            if 'error' in r:
                print(f"  {Colors.RED}Error: {r['error']}{Colors.END}")
        else:
            # Optional: show results for passed tests
            if 'results' in r:
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
        print(f"\n{Colors.GREEN}{Colors.BOLD}All tests passed! 🎉{Colors.END}")


if __name__ == "__main__":
    summary = []

    # Normal tests
    for file_path, expected in tests.items():
        if os.path.exists(file_path):
            result = run_test(file_path, expected)
            summary.append(result)
        else:
            print(f"{Colors.YELLOW}⚠️ File not found: {file_path}{Colors.END}")

    # Contradiction tests
    for file_path in contradiction_tests:
        if os.path.exists(file_path):
            result = run_contradiction_test(file_path)
            summary.append(result)
        else:
            print(f"{Colors.YELLOW}⚠️ File not found: {file_path}{Colors.END}")

    print_summary(summary)