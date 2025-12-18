from .parser import Parser
from .data import *
from .lexer import tokenize
from typing import List, Set, Union, Iterable
import sys
from pathlib import Path


# =========
# FILE CONTENT PARSING
# =========
def parse_input_lines(lines: Iterable[str]) -> ParseResult:
	rules: List[Union[Implies, Equiv]] = []
	initial_facts: Set[str] = set()
	queries: List[Ident] = []
	symbols: Set[Ident] = set()
	original_rules: List[str] = []
	duplicate_rules: Set[str] = set()
	duplicate_queries: Set[str] = set()
	duplicate_facts: Set[str] = set()
	seen_rule_text: Set[str] = set()
	seen_query_names: Set[str] = set()

	def collect(e: Expr):
		if isinstance(e, Ident):
			for ch in e.name:
				if "A" <= ch <= "Z":
					symbols.add(Ident(ch))
		elif isinstance(e, (And, Or, Xor)):
			for t in e.terms:
				collect(t)
		elif isinstance(e, Not):
			collect(e.child)

	for raw in lines:
		# Strip inline comments and surrounding whitespace
		cleaned = raw.split("#", 1)[0].strip()
		line = cleaned
		if not line:
			continue

		# Initial facts: =ABCD
		if line.startswith("="):
			for ch in line[1:].strip():
				if ch == " ":
					continue
				if not ("A" <= ch <= "Z"):
					raise ValueError(f"Invalid initial fact {ch!r} in line: {raw.strip()}")
				if ch in initial_facts:
					duplicate_facts.add(ch)
				initial_facts.add(ch)
				symbols.add(Ident(ch))
			continue

		# Queries: ?XYZ
		if line.startswith("?"):
			for ch in line[1:].strip():
				if ch == " ":
					continue
				if not ("A" <= ch <= "Z"):
					raise ValueError(f"Invalid query {ch!r} in line: {raw.strip()}")
				ident = Ident(ch)
				if ident.name in seen_query_names:
					duplicate_queries.add(ident.name)
				else:
					queries.append(ident)
					seen_query_names.add(ident.name)
				symbols.add(ident)
			continue

		# Rule or equivalence
		normalized_rule = line.strip()
		if normalized_rule in seen_rule_text:
			duplicate_rules.add(normalized_rule)
		else:
			seen_rule_text.add(normalized_rule)
		original_rules.append(cleaned)
		toks = tokenize(line)
		p = Parser(toks)
		if any(t.type == "EQUIV" for t in toks):
			eq = p.parse_equiv_line()
			rules.append(eq)
			collect(eq.left)
			collect(eq.right)
		else:
			imp = p.parse_rule_line()
			rules.append(imp)
			collect(imp.premise)
			collect(imp.conclusion)

	if duplicate_facts:
		dupes = " ".join(sorted(duplicate_facts))
		raise ValueError(f"Duplicate or contradictory initial facts: {dupes}")
	if duplicate_queries:
		dupes = " ".join(sorted(duplicate_queries))
		raise ValueError(f"Duplicate queries: {dupes}")
	if duplicate_rules:
		dupes = "; ".join(sorted(duplicate_rules))
		raise ValueError(f"Duplicate rules: {dupes}")
	if not rules:
		raise ValueError("No rules provided in input")
	if not queries:
		raise ValueError("No queries provided in input")

	return ParseResult(rules, initial_facts, queries, symbols, original_rules)


# =========
# FILE LOADER
# =========
# Reads input file and return lines.
# Errors handled:
# - File not found
# - Permission denied
# - Empty file (no non-whitespace content)
def read_lines_from_file(path: str) -> List[str]:
	p = Path(path)
	try:
		text = p.read_text(encoding="utf-8")
	except FileNotFoundError as e:
		raise ValueError(f"No such file: {path}") from e
	except PermissionError as e:
		raise ValueError(f"Permission denied: {path}") from e

	# Check empty (no non-whitespace content)
	if not text or not any(ch.strip() for ch in text.splitlines()):
		raise ValueError(f"Empty file: {path}")

	return text.splitlines()


def parser(path: str) -> ParseResult:
	# Parse file given by path, otherwise default example
	default_path = "inputs/example.txt"
	path = path if len(path) > 1 else default_path
	try:
		lines = read_lines_from_file(path)
	except ValueError as e:
		print(f"Error: {e}")
		sys.exit(1)

	try:
		pr = parse_input_lines(lines)
	except ValueError as e:
		print(f"Error: {e}")
		sys.exit(1)

	# Set identifiers value based on facts
	pr.set_identifiers()

	return pr
