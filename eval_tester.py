from execution.exec import Engine
from parsing.file_utils import parser
import os

tests = {
    # And conclusions
    "inputs/eval_tests/and_conclusions/1.txt": {
        "A": True,
        "F": True,
        "K": True,
        "P": True
    },
    "inputs/eval_tests/and_conclusions/2.txt": {
        "A": True,
        "F": True,
        "K": False,
        "P": True
    },
    # Or conditions
    "inputs/eval_tests/or_conditions/3.txt": {
        "A": False
    },
    "inputs/eval_tests/or_conditions/4.txt": {
        "A": True
    },
    "inputs/eval_tests/or_conditions/5.txt": {
        "A": True
    },
    "inputs/eval_tests/or_conditions/6.txt": {
        "A": True
    },
    # Xor conditions
    "inputs/eval_tests/xor_conditions/7.txt": {
        "A": False
    },
    "inputs/eval_tests/xor_conditions/8.txt": {
        "A": True
    },
    "inputs/eval_tests/xor_conditions/9.txt": {
        "A": True
    },
    "inputs/eval_tests/xor_conditions/10.txt": {
        "A": False
    },
    # Negation
    "inputs/eval_tests/negation/12.txt": {
        "A": False
    },
    "inputs/eval_tests/negation/13.txt": {
        "A": True
    },
    "inputs/eval_tests/negation/14.txt": {
        "A": False
    },
    "inputs/eval_tests/negation/15.txt": {
        "A": False
    },
    # Same conclusion
    "inputs/eval_tests/same_conclusion/16.txt": {
        "A": False
    },
    "inputs/eval_tests/same_conclusion/17.txt": {
        "A": True
    },
    "inputs/eval_tests/same_conclusion/18.txt": {
        "A": True
    },
    "inputs/eval_tests/same_conclusion/19.txt": {
        "A": True
    },
    # Parentheses
    "inputs/eval_tests/parentheses/20.txt": {
        "E": False
    },
    "inputs/eval_tests/parentheses/21.txt": {
        "E": True
    },
    "inputs/eval_tests/parentheses/22.txt": {
        "E": False
    },
    "inputs/eval_tests/parentheses/23.txt": {
        "E": False
    },
    "inputs/eval_tests/parentheses/24.txt": {
        "E": False
    },
    "inputs/eval_tests/parentheses/25.txt": {
        "E": True
    },
    "inputs/eval_tests/parentheses/26.txt": {
        "E": False
    },
    "inputs/eval_tests/parentheses/27.txt": {
        "E": False
    },
    "inputs/eval_tests/parentheses/28.txt": {
        "E": False
    },
    "inputs/eval_tests/parentheses/29.txt": {
        "E": True
    },
    "inputs/eval_tests/parentheses/30.txt": {
        "E": True
    }
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
    
    print("Failed Tests:")
    for r in summary:
        if not r['passed']:
            print(f"{r['file']}")
