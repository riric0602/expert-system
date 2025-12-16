from execution.exec import Engine
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
        "D": None,
        "E": False,
        "F": True,
        "X": True,
        "Y": None,
        "Z": True
    },
    # Complex tests
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
    "inputs/complex_tests/negation/4.txt": {
        "B": True,
        "C": True,
    },
    "inputs/complex_tests/negation/5.txt": {
        "B": False,
        "C": False,
    },
    "inputs/complex_tests/negation/6.txt": {
        "B": False,
        "C": False,
    },
    "inputs/complex_tests/or_conditions/7.txt": {
        "C": False,
    },
    "inputs/complex_tests/or_conditions/8.txt": {
        "E": False,
    },
    "inputs/complex_tests/or_conditions/9.txt": {
        "F": True,
    },
    "inputs/complex_tests/or_conditions/10.txt": {
        "C": True,
        "D": True,
        "F": False
    },
    "inputs/complex_tests/parentheses/11.txt": {
        "C": True,
        "E": False
    },
    "inputs/complex_tests/parentheses/12.txt": {
        "D": True,
        "E": False
    },
    "inputs/complex_tests/parentheses/13.txt": {
        "E": False,
        "H": True
    },
    "inputs/complex_tests/parentheses/14.txt": {
        "D": True,
        "F": True
    },
    "inputs/complex_tests/parentheses/15.txt": {
        "A": True,
        "B": False,
        "C": True
    },
    "inputs/complex_tests/parentheses/16.txt": {
        "B": True,
        "C": False,
        "E": False
    },
}

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

if __name__ == "__main__":
    summary = []
    
    for file_path, expected in tests.items():
        if os.path.exists(file_path):
            result = run_test(file_path, expected)
            summary.append(result)
        else:
            print(f"File {file_path} not found.")

    # Print results
    for r in summary:
        print(f"Test: {r['file']}")
        print(f"Passed: {'✅' if r['passed'] else '❌'}")
        if not r['passed']:
            for k in r['results']:
                if r['results'][k] != r['expected'].get(k):
                    print("Results vs Expected:")
                    print(f"  {k}: got {r['results'][k]}, expected {r['expected'].get(k)}")
        print("---------------------------------------------------------")
