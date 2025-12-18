#!/usr/bin/env python3

from typing import List, Optional, Union
from .data import	Expr,	\
					And, \
					Or, \
					Xor, \
					Ident, \
					Not, \
					And, \
					Implies, \
					Equiv
from .lexer import Token

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
