from execution.exec import Engine
from parsing.file_utils import parser

if __name__ == "__main__":
    # Parse file provided as first argument, otherwise default example
    default_path = "inputs/example.txt"
    pr = parser(default_path)
    for s in pr.original_rules:
        print(s)
    for r in pr.rules:
        print(" -", r)

    print("Initial facts:", pr.initial_facts)	
    print(f"Queries: {pr.queries}")
    print("Symbols:", pr.symbols)
    print("---------------------------------------------------------")

    engine = Engine(pr)
    engine.backward_chaining()

    print("---------------------------------------------------------")
    for q in pr.queries:
        print(f"{q.name}: {q.value}")
