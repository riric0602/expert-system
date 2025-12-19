import argparse
import sys
import os
from typing import Dict, Iterable, List, Optional
from parsing.data import Ident
from parsing.file_utils import parser, parse_input_lines, read_lines_from_file
from execution.exec import Engine
from execution.exec import Engine, ContradictionException
from tester.tester import Colors, print_summary, run_test, run_contradiction_test, tests, contradiction_tests


def parse_args():
    parser = argparse.ArgumentParser(description="Expert system: Backward Chaining algorithm")
    parser.add_argument(
        "input_file",
        nargs="?",
        help="Path to the input file.",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Launch the interactive prompt instead of the CLI demo.",
    )
    parser.add_argument(
        "--tester",
        action="store_true",
        help="Launch the tester to verify execution.",
    )
    parser.add_argument(
        "--logs",
        action="store_true",
        default=False,
        help="Display reasoning logs to understand the solutions.",
    )
    return parser.parse_args()


def run_main(pr, file_path, logging):
    engine = Engine(pr, logging)
    results = engine.backward_chaining()

    # Display the logs
    if logging:
        with open(file_path, "r") as f:
            print(f.read())
        with open("reasoning.log", "r") as f:
            print(f.read())

    print("Query results:")
    for q in results:
        print(f"  {q.name}: {q.value}")


def run_tester():
    summary = []

    # Normal tests
    for file_path, expected in tests.items():
        if os.path.exists(file_path):
            result = run_test(file_path, expected)
            summary.append(result)
        else:
            print(f"{Colors.YELLOW}⚠️ File not found: {file_path}{Colors.END}")

    # Contradiction tests
    for file_path in contradiction_tests:
        if os.path.exists(file_path):
            result = run_contradiction_test(file_path)
            summary.append(result)
        else:
            print(f"{Colors.YELLOW}⚠️ File not found: {file_path}{Colors.END}")

    print_summary(summary)


def load_program_lines(path: Optional[str]) -> List[str]:
    return read_lines_from_file(path)


def load_parse_result(lines: Iterable[str]):
    pr = parse_input_lines(lines)
    pr.set_identifiers()
    return pr


def run_inference(base_lines: List[str], fact_overrides: Dict[str, Optional[bool]]):
    pr = load_parse_result(base_lines)

    # Apply overrides to known identifiers
    for ident in pr.symbols:
        if ident.name in fact_overrides:
            ident.value = fact_overrides[ident.name]
    for q in pr.queries:
        if q.name in fact_overrides:
            q.value = fact_overrides[q.name]

    # Add user-created facts that weren't in the original program
    for name, value in fact_overrides.items():
        if name not in {i.name for i in pr.symbols}:
            pr.symbols.add(Ident(name, value))

    engine = Engine(pr)
    try:
        engine.backward_chaining()
    except SystemExit:
        # engine.backward_chaining calls exit() on errors; keep the window alive instead.
        raise RuntimeError("Inference halted due to an error. Check your rules.")

    queries = {q.name: q.value for q in pr.queries}
    facts = {ident.name: ident.value for ident in pr.symbols}
    return queries, facts


def launch_interactive_prompt(base_lines: List[str], base_parse_result):
    def value_label(v: Optional[bool]) -> str:
        if v is True:
            return "true"
        if v is False:
            return "false"
        return "none"

    def prompt_fact_name() -> Optional[str]:
        try:
            name = input(" Fact (A-Z): ").strip().upper()
        except EOFError:
            print()
            return None

        if not name:
            print(" Please enter a fact name.")
            return None
        if len(name) != 1 or not name.isalpha() or not name.isupper():
            print(" Use a single uppercase letter (A-Z).")
            return None
        return name

    def prompt_fact_value() -> Optional[bool]:
        while True:
            try:
                raw = input(" Value (true/false/none): ").strip().lower()
            except EOFError:
                print()
                return None

            if raw in {"true", "t", "yes", "y", "1"}:
                return True
            if raw in {"false", "f", "no", "n", "0"}:
                return False
            if raw in {"none", "null", ""}:
                return None
            print(" Enter true, false, or none.")

    def print_fact_values():
        print(" Current facts:")
        for name in sorted(fact_values.keys()):
            print(f"  - {name} = {value_label(fact_values[name])}")
        if not fact_values:
            print("  (none)")

    fact_values: Dict[str, Optional[bool]] = {
        ident.name: ident.value for ident in base_parse_result.symbols
    }

    print("Interactive mode. Commands: ADD, MODIFY, REMOVE, QUERY, LIST, HELP, EXIT")
    print_fact_values()

    while True:
        try:
            raw_cmd = input("expert> ").strip().upper()
        except EOFError:
            print()
            break

        if not raw_cmd:
            continue

        if raw_cmd == "ADD":
            name = prompt_fact_name()
            if not name:
                continue
            if name in fact_values:
                print(f" Fact {name} already exists.")
                continue
            fact_values[name] = None
            print(f" Added fact {name} with value none.")
            print_fact_values()

        elif raw_cmd == "MODIFY":
            name = prompt_fact_name()
            if not name:
                continue
            if name not in fact_values:
                print(f" Fact {name} does not exist. Use ADD to create it.")
                continue
            value = prompt_fact_value()
            fact_values[name] = value
            print(f" Set {name} = {value_label(value)}.")
            print_fact_values()

        elif raw_cmd == "REMOVE":
            name = prompt_fact_name()
            if not name:
                continue
            if name not in fact_values:
                print(f" Fact {name} does not exist.")
                continue
            fact_values.pop(name, None)
            print(f" Removed fact {name}.")
            print_fact_values()

        elif raw_cmd == "QUERY":
            try:
                queries, facts = run_inference(base_lines, fact_values)
            except Exception as e:
                print(f" Error during inference: {e}")
                continue

            print(" Query results:")
            for name in sorted(queries.keys()):
                print(f"  - {name}: {value_label(queries[name])}")

            print(" Facts after inference:")
            for name in sorted(facts.keys()):
                print(f"  - {name}: {value_label(facts[name])}")

        elif raw_cmd == "LIST":
            print_fact_values()

        elif raw_cmd in {"HELP", "H"}:
            print(" Commands:")
            print("  ADD    - Add a new fact (value starts as none)")
            print("  MODIFY - Change an existing fact to true/false/none")
            print("  REMOVE - Remove an existing fact")
            print("  QUERY  - Run the inference engine with current facts")
            print("  LIST   - Show current facts and values")
            print("  EXIT   - Quit interactive mode")

        elif raw_cmd in {"EXIT", "QUIT"}:
            print(" Bye.")
            break

        else:
            print(f" Unknown command: {raw_cmd}. Type HELP for options.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <file_path>")
        sys.exit(1)

    args = parse_args()

    try:
        if args.tester:
            run_tester()
        else:
            if not args.input_file:
                raise ValueError("Interactive mode requires an input file!")
            
            file_path = args.input_file
            logging = args.logs
            parse_result = parser(file_path)

            if args.interactive:
                launch_interactive_prompt(load_program_lines(file_path), parse_result)
            else:
                run_main(parse_result, file_path, logging)

    except ContradictionException as e:
        print(f"Contradiction detected {e}")
        sys.exit(1)
    except Exception as e:
        print(e)
        raise
