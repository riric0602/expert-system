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
    ?ED
    """.strip("\n")

    pr = parse_input_lines(text.splitlines())

    # Set identifiers value based on facts
    pr.set_identifiers()

    print("Rules (desugared):")
    for r in pr.rules:
        print(" -", r)
    print("Initial facts:", pr.initial_facts)	
    print(f"Queries: {pr.queries}")
    print("Symbols:", "".join(x.name for x in sorted(pr.symbols, key=lambda x: x.name)))
    print("---------------------------------------------------------")

    backward_chaining(pr)

    print("---------------------------------------------------------")
    for q in pr.queries:
        print(f"{q.name}: {'True' if q.value else 'False'}")
