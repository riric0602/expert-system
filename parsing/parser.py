#!/usr/bin/env python3

from typing import List, Optional, Set, Union, Iterable
from data import	Expr,	\
					And, \
					Or, \
					Xor, \
					Ident, \
					Not, \
					And, \
					Implies, \
					Eqv, \
					ParseResult
from lexer import Token, tokenize

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
	# conclusion := IDENT ( 'AND' IDENT )*

	def parse_rule_line(self) -> Implies:
		prem = self.parse_expr()
		self.eat("IMPLIES")
		concl = self.parse_conclusion()
		return Implies(premise=prem, conclusion=concl)

	def parse_equiv_line(self) -> List[Implies]:
		# Parse A <=> B, then RETURN TWO implies: A=>B and B=>A
		left = self.parse_expr()
		self.eat("EQUIV")
		right = self.parse_expr()
		return [Implies(premise=left, conclusion=right),
				Implies(premise=right, conclusion=left)]

	def parse_conclusion(self) -> Expr:
		if not self.at("IDENT"):
			t = self.cur()
			where = t.index if t else -1
			got = t.type if t else "EOF"
			raise ValueError(f"Conclusion must start with IDENT, got {got} at {where}")
		names: List[str] = [self.eat("IDENT").value]
		while self.at("AND"):
			self.eat("AND")
			if not self.at("IDENT"):
				raise ValueError("AND in conclusion must be followed by IDENT")
			names.append(self.eat("IDENT").value)
		idents = [Ident(n) for n in names]
		return idents[0] if len(idents) == 1 else And(idents)
# ---- End of Parser class ----

# =========
# FILE CONTENT PARSING
# =========
def parse_input_lines(lines: Iterable[str]) -> ParseResult:
	rules: List[Implies] = []
	initial_facts: Set[str] = set()
	queries: List[Ident] = []
	symbols: Set[Ident] = set()

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
				queries.append(ident)
				symbols.add(ident)
			continue

		# Rule or equivalence
		toks = tokenize(line)
		p = Parser(toks)
		if any(t.type == "EQUIV" for t in toks):
			two = p.parse_equiv_line()	# returns [Implies(left=>right), Implies(right=>left)]
			rules.extend(two)
			for imp in two:
				collect(imp.premise)
				collect(imp.conclusion)
		else:
			imp = p.parse_rule_line()
			rules.append(imp)
			collect(imp.premise)
			collect(imp.conclusion)

	return ParseResult(rules, initial_facts, queries, symbols)

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

def pretty_rule(r: Implies) -> str:
	return f"{pretty_expr(r.premise)} => {pretty_expr(r.conclusion)}"

# =========
# TEST MAIN
# =========
if __name__ == "__main__":
	# TODO Remove and parse file
	text = """
	# rules
	A + (B | C) => D
	!(A + B) | (C ^ D) => E
	A <=> B
	A => B + C

	# initial facts
	=AB

	# queries
	?DEZ
	""".strip("\n")

	pr = parse_input_lines(text.splitlines())

	# Set identifiers value based on facts
	pr.set_identifiers()

	print("Rules (desugared):")
	for r in pr.rules:
		print(" -", pretty_rule(r))
	# Pretty print other sections using the same ident=value style
	print("Initial facts:", " ".join(f"{s.name}={s.value}" for s in sorted(pr.symbols, key=lambda x: x.name) if s.value))
	print("Queries:", " ".join(f"{q.name}={q.value}" for q in sorted(pr.queries, key=lambda x: x.name)))
	print("Symbols:", " ".join(f"{s.name}={s.value}" for s in sorted(pr.symbols, key=lambda x: x.name)))
