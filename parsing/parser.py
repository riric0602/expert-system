#!/usr/bin/env python3

import sys
from pathlib import Path
from typing import List, Optional, Set, Union, Iterable

# Allow running as a script or as part of the parsing package
if __package__ is None:
	sys.path.append(str(Path(__file__).resolve().parent.parent))

from parsing.data import	Expr,	\
							And, \
							Or, \
							Xor, \
							Ident, \
							Not, \
							And, \
							Implies, \
							Equiv, \
							ParseResult
from parsing.lexer import Token, tokenize

# =========
# PARSER CLASS
# =========
class Parser:
	def __init__(self, tokens: List[Token]):
		self.tokens = tokens
		self.i = 0

	def at(self, *kinds: str) -> bool:
		return self.i < len(self.tokens) and self.tokens[self.i].type in kinds

	def cur(self) -> Optional[Token]:
		return self.tokens[self.i] if self.i < len(self.tokens) else None

	def eat(self, kind: str) -> Token:
		t = self.cur()
		if not t or t.type != kind:
			where = t.index if t else -1
			got = t.type if t else "EOF"
			raise ValueError(f"Expected {kind}, got {got} at {where}")
		self.i += 1
		return t

	# ----- Expression grammar with precedence -----
	# expr := or_expr
	# or_expr := xor_expr ( 'OR' xor_expr )*
	# xor_expr := and_expr ( 'XOR' and_expr )*
	# and_expr := unary ( 'AND' unary )*
	# unary := 'NOT' unary | primary
	# primary := IDENT | '(' expr ')'

	def parse_expr(self) -> Expr:
		return self.parse_or()

	def parse_or(self) -> Expr:
		left = self.parse_xor()
		terms = [left]
		while self.at("OR"):
			self.eat("OR")
			terms.append(self.parse_xor())
		return terms[0] if len(terms) == 1 else Or(terms)

	def parse_xor(self) -> Expr:
		left = self.parse_and()
		terms = [left]
		while self.at("XOR"):
			self.eat("XOR")
			terms.append(self.parse_and())
		return terms[0] if len(terms) == 1 else Xor(terms)

	def parse_and(self) -> Expr:
		left = self.parse_unary()
		terms = [left]
		while self.at("AND"):
			self.eat("AND")
			terms.append(self.parse_unary())
		return terms[0] if len(terms) == 1 else And(terms)

	def parse_unary(self) -> Expr:
		if self.at("NOT"):
			self.eat("NOT")
			return Not(self.parse_unary())
		return self.parse_primary()

	def parse_primary(self) -> Expr:
		if self.at("IDENT"):
			name = self.eat("IDENT").value
			return Ident(name)
		if self.at("LPAREN"):
			self.eat("LPAREN")
			node = self.parse_expr()
			self.eat("RPAREN")
			return node
		t = self.cur()
		where = t.index if t else -1
		got = t.type if t else "EOF"
		raise ValueError(f"Expected IDENT or '(', got {got} at {where}")

	# ----- Rule line parsers -----
	# rule_line := expr 'IMPLIES' conclusion
	# equiv_line := expr 'EQUIV' expr
	# conclusion := expr  (allow NOT/OR/XOR in conclusions too)

	def parse_rule_line(self) -> Implies:
		prem = self.parse_expr()
		self.eat("IMPLIES")
		concl = self.parse_conclusion()
		return Implies(premise=prem, conclusion=concl)

	def parse_equiv_line(self) -> Equiv:
		# Parse A <=> B, return an Equiv node
		left = self.parse_expr()
		self.eat("EQUIV")
		right = self.parse_expr()
		return Equiv(left=left, right=right)

	def parse_conclusion(self) -> Expr:
		# Use full expression grammar so conclusions can include NOT and other operators.
		return self.parse_expr()
# ---- End of Parser class ----

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
		line = raw.strip()
		if not line or line.startswith("#"):
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
		original_rules.append(raw)
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

# =========
# DEBUG PRINT
# =========
def pretty_expr(e: Expr) -> str:
	if isinstance(e, Ident):
		# Include the current boolean value of the identifier
		return f"{e.name}={e.value}"
	if isinstance(e, Not):
		return f"!{pretty_expr(e.child)}"
	if isinstance(e, And):
		return " + ".join(pretty_expr(t) for t in e.terms)
	if isinstance(e, Or):
		return " | ".join(pretty_expr(t) for t in e.terms)
	if isinstance(e, Xor):
		return " ^ ".join(pretty_expr(t) for t in e.terms)
	return "<??>"

def pretty_rule(r: Union[Implies, Equiv]) -> str:
	if isinstance(r, Implies):
		return f"{pretty_expr(r.premise)} => {pretty_expr(r.conclusion)}"
	# Equivalence
	return f"{pretty_expr(r.left)} <=> {pretty_expr(r.right)}"

def parser(path: str) -> ParseResult:
	# Parse file given by path, otherwise default example
	default_path = Path(__file__).resolve().parent / "examples" / "example.txt"
	path = path if path else str(default_path)
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

# # =========
# # TEST MAIN
# # =========
if __name__ == "__main__":
	# Parse file provided as first argument, otherwise default example
	default_path = Path(__file__).resolve().parent / "examples" / "example.txt"
	input_path = sys.argv[1] if len(sys.argv) > 1 else str(default_path)
	pr = parser(input_path)
	for s in pr.original_rules:
		print(s)
	print("Rules:")
	for r in pr.rules:
		print(" -", pretty_rule(r))

	# Pretty print other sections using the same ident=value style
	print("Initial facts:", " ".join(f"{s.name}={s.value}" for s in sorted(pr.symbols, key=lambda x: x.name) if s.value))
	print("Queries:", " ".join(f"{q.name}={q.value}" for q in sorted(pr.queries, key=lambda x: x.name)))
	print("Symbols:", " ".join(f"{s.name}={s.value}" for s in sorted(pr.symbols, key=lambda x: x.name)))
	print("")
	print(str(pr.rules))
