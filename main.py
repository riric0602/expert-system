from parsing.parser import parse_input_lines
from execution.exec import backward_chaining

if __name__ == "__main__":
    text = """
    # rules
    C => E
    A + (B | C) => D
    !(A + B) | (C ^ D) => E
    A <=> B
    A => B + C

    # initial facts
    =AB

    # queries
    ?EDE
    """.strip("\n")

    pr = parse_input_lines(text.splitlines())

    # Set identifiers value based on facts
    pr.set_identifiers()

    print("Rules (desugared):")
    for r in pr.rules:
        print(" -", r)
    print("Initial facts:", pr.initial_facts)	
    print(f"Queries: {pr.queries}")
    print("Symbols:", "".join(sorted(pr.symbols)))
    print("---------------------------------------------------------")

    backward_chaining(pr)
