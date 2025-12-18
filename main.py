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
    parser = argparse.ArgumentParser(description="Expert system: Backward Chaning algorithm")
    parser.add_argument(
        "input_file",
        nargs="?",
        help="Path to the input file.",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Launch the interactive window instead of the CLI demo.",
    )
    parser.add_argument(
        "--tester",
        action="store_true",
        help="Launch the tester to verify execution.",
    )
    return parser.parse_args()


def run_main(pr):
    engine = Engine(pr)
    results = engine.backward_chaining()
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


def launch_interactive_window(base_lines: List[str], base_parse_result):
    import tkinter as tk
    from tkinter import messagebox

    def value_label(v: Optional[bool]) -> str:
        if v is True:
            return "true"
        if v is False:
            return "false"
        return "none"

    fact_values: Dict[str, Optional[bool]] = {
        ident.name: ident.value for ident in base_parse_result.symbols
    }

    def refresh_list():
        items = [
            f"{name} = {value_label(fact_values[name])}"
            for name in sorted(fact_values.keys())
        ]
        list_var.set(items)

    def selected_fact() -> Optional[str]:
        selection = fact_list.curselection()
        if not selection:
            return None
        line = fact_list.get(selection[0])
        return line.split("=", 1)[0].strip()

    def set_fact_value(val: Optional[bool]):
        name = selected_fact()
        if not name:
            messagebox.showinfo("Pick a fact", "Select a fact to update.")
            return
        fact_values[name] = val
        refresh_list()

    def remove_fact():
        name = selected_fact()
        if not name:
            messagebox.showinfo("Remove fact", "Select a fact to remove.")
            return
        fact_values.pop(name, None)
        refresh_list()

    def add_fact():
        name = add_entry.get().strip().upper()
        if not name or len(name) != 1 or not name.isalpha() or not name.isupper():
            messagebox.showerror("Invalid fact", "Use a single uppercase letter (A-Z).")
            return
        if name in fact_values:
            messagebox.showinfo("Exists", f"Fact {name} is already listed.")
            return
        fact_values[name] = None
        add_entry.delete(0, tk.END)
        refresh_list()

    def run_and_render():
        try:
            queries, facts = run_inference(base_lines, fact_values)
        except Exception as e:
            render_result(f"Error: {e}")
            return

        lines = ["Query results:"]
        for name in sorted(queries.keys()):
            lines.append(f" - {name}: {value_label(queries[name])}")

        lines.append("")
        lines.append("Facts after inference:")
        for name in sorted(facts.keys()):
            lines.append(f" - {name}: {value_label(facts[name])}")

        render_result("\n".join(lines))

    def render_result(text: str):
        output.configure(state="normal")
        output.delete("1.0", tk.END)
        output.insert(tk.END, text)
        output.configure(state="disabled")

    root = tk.Tk()
    root.title("Expert System (interactive)")

    list_var = tk.StringVar(value=[])

    top_frame = tk.Frame(root)
    top_frame.pack(fill="both", expand=True, padx=12, pady=12)

    left = tk.Frame(top_frame)
    left.pack(side="left", fill="y")

    tk.Label(left, text="Facts").pack(anchor="w")
    fact_list = tk.Listbox(left, listvariable=list_var, width=24, height=14)
    fact_list.pack(fill="y", expand=True)

    controls = tk.Frame(top_frame)
    controls.pack(side="left", padx=12)

    tk.Label(controls, text="Set value").pack(anchor="w")
    tk.Button(controls, text="True", width=10, command=lambda: set_fact_value(True)).pack(pady=2)
    tk.Button(controls, text="False", width=10, command=lambda: set_fact_value(False)).pack(pady=2)
    tk.Button(controls, text="None", width=10, command=lambda: set_fact_value(None)).pack(pady=2)
    tk.Button(controls, text="Remove", width=10, command=remove_fact).pack(pady=(8, 2))

    add_frame = tk.Frame(controls)
    add_frame.pack(pady=(12, 0), fill="x")
    tk.Label(add_frame, text="Add fact (A-Z)").pack(anchor="w")
    add_entry = tk.Entry(add_frame, width=12)
    add_entry.pack(side="left", pady=2)
    tk.Button(add_frame, text="Add", command=add_fact).pack(side="left", padx=4)

    tk.Button(controls, text="Evaluate queries", command=run_and_render).pack(pady=12, fill="x")

    right = tk.Frame(top_frame)
    right.pack(side="left", fill="both", expand=True)
    tk.Label(right, text="Results").pack(anchor="w")
    output = tk.Text(right, height=16, width=48, state="disabled")
    output.pack(fill="both", expand=True)

    refresh_list()
    root.mainloop()


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
            parse_result = parser(file_path)

            if args.interactive:
                launch_interactive_window(load_program_lines(file_path), parse_result)
            else:
                run_main(parse_result)
    except ContradictionException as e:
        print(f"Contradiction detected {e}")
        sys.exit(1)
    except Exception as e:
        print(e)
        raise

