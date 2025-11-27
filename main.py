from parsing.parser import parse_input_lines
from execution.exec import Engine

if __name__ == "__main__":
    text = """
# rules
A <=> B
E <=> G
A + D => E
!(B + C) | (D ^ H) => F
E => G

# initial facts
=AC

# queries
?FG
    """.strip("\n")

    pr = parse_input_lines(text.splitlines())

    # Set identifiers value based on facts
    pr.set_identifiers()

    print("Rules (desugared):")
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
