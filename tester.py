from execution.exec import Engine, ContradictionException
from parsing.file_utils import parser
import os

tests = {
    # Unit tests
    # "inputs/unit_tests/and_rules.txt": {
    #     "C": True,
    #     "D": True,
    #     "E": False,
    #     "F": False,
    #     "I": False,
    #     "J": False,
    # },
    # "inputs/unit_tests/or_rules.txt": {
    #     "C": True,
    #     "D": True,
    #     "E": False,
    #     "F": False,
    #     "I": True,
    #     "J": True,
    #     "K": True,
    #     "L": True
    # },
    # "inputs/unit_tests/xor_rules.txt": {
    #     "C": False,
    #     "D": False,
    #     "E": False,
    #     "F": False,
    #     "I": True,
    #     "J": True,
    #     "K": False,
    #     "L": False
    # },
    # "inputs/unit_tests/not_rules.txt": {
    #     "D": None,
    #     "E": False,
    #     "F": True,
    #     "X": True,
    #     "Y": None,
    #     "Z": True
    # },
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
    }
}

contradiction_tests = [
    "inputs/complex_tests/contradictions/1.txt",
    "inputs/complex_tests/contradictions/2.txt",
    "inputs/complex_tests/contradictions/3.txt"
]


def run_test(file_path, expected):
    pr = parser(file_path)
    engine = Engine(pr)
    results = engine.backward_chaining()
    
    output = {}
    passed = True
    for q in results:
        output[q.name] = q.value
        expected_val = expected.get(q.name)
        if expected_val is not None and q.value != expected_val:
            passed = False
    
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

        return {
            "file": file_path,
            "passed": False,
            "error": "No ContradictionException was raised"
        }

    except ContradictionException:
        return {
            "file": file_path,
            "passed": True
        }

    except Exception as e:
        return {
            "file": file_path,
            "passed": False,
            "error": f"Unexpected exception: {type(e).__name__}"
        }



if __name__ == "__main__":
    summary = []

    # Normal tests
    for file_path, expected in tests.items():
        if os.path.exists(file_path):
            print(file_path)
            result = run_test(file_path, expected)
            summary.append(result)
        else:
            print(f"File {file_path} not found.")

    # Contradiction tests
    for file_path in contradiction_tests:
        if os.path.exists(file_path):
            print(file_path)
            result = run_contradiction_test(file_path)
            summary.append(result)
        else:
            print(f"File {file_path} not found.")

    # ------------------- Print results -------------------
    for r in summary:
        print(f"Test: {r['file']}")
        print(f"Passed: {'✅' if r['passed'] else '❌'}")

        # Only print details if failed
        if not r['passed']:
            if 'results' in r and 'expected' in r:
                for k in r['results']:
                    expected_val = r['expected'].get(k)
                    if expected_val is not None and r['results'][k] != expected_val:
                        print(f"  {k}: got {r['results'][k]}, expected {expected_val}")
            if 'error' in r:
                print(f"  Error: {r['error']}")

        print("---------------------------------------------------------")
