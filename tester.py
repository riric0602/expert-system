from execution.exec import Engine
from parsing.file_utils import parser
import os

# Define tests: map input file to expected query results
tests = {
    "inputs/and_rules.txt": {
        "C": True,
        "D": True,
        "E": None,
        "F": False,
        "I": None,
        "J": False,
    },
    "inputs/or_rules.txt": {
        "C": True,
        "D": True,
        "E": None,
        "F": False,
        "I": True,
        "J": True,
        "K": True,
        "L": True
    },
    "inputs/xor_rules.txt": {
        "C": None,
        "D": False,
        "E": None,
        "F": False,
        "X": True,
        "Z": True,
        "Y": None,
        "W": False
    },
    "inputs/not_rules.txt": {
        "D": None,
        "E": False,
        "F": True,
        "X": True,
        "Y": None,
        "Z": True
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
        print("Results vs Expected:")
        for k in r['results']:
            print(f"  {k}: got {r['results'][k]}, expected {r['expected'].get(k)}")
        print("---------------------------------------------------------")
