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

    # text = """
    # # rules
    # C => E
    # A + B + C => D
    # A | B => C
    # A + !B => F
    # C | !G => H
    # V ^ W => X  
    # A + B => Y + Z
    # C | D => X | V
    # A + B <=> C
    # A + B <=> !C

    # =ABG

    # ?C
    #     """.strip("\n")

    # pr = parse_input_lines(text.splitlines())

    # # Set identifiers value based on facts
    # pr.set_identifiers()

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
