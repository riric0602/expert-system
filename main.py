from execution.exec import Engine
from parsing.file_utils import parser, parse_input_lines
import sys

if __name__ == "__main__":
    # Parse file provided as first argument, otherwise default example
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = "inputs/example.txt"
        
    pr = parser(path)

    for s in pr.original_rules:
        print(s)
    for r in pr.rules:
        print(" -", r)

    print("Initial facts:", pr.initial_facts)	
    print(f"Queries: {pr.queries}")
    print("Symbols:", pr.symbols)
    print("---------------------------------------------------------")

    engine = Engine(pr)
    results = engine.backward_chaining()

    print("---------------------------------------------------------")
    for q in results:
        print(f"{q.name}: {q.value}")
