from dataclasses import dataclass
from typing import List, Set, Union

# Expr nodes
class Expr: pass

@dataclass
class Ident(Expr):
	name: str	# 'A'-'Z'
	value: bool = False

@dataclass
class Not(Expr):
	child: Expr

@dataclass
class And(Expr):
	terms: List[Expr]

@dataclass
class Or(Expr):
	terms: List[Expr]

@dataclass
class Xor(Expr):
	terms: List[Expr]

@dataclass
class Implies:
	premise: Expr
	conclusion: Expr

@dataclass
class Eqv:
	left: Expr
	right: Expr

# Parsing result
@dataclass
class ParseResult:
	rules: List[Union[Implies, Eqv]]
	initial_facts: Set[str]
	queries: List[str]
	symbols: Set[str]

	# Post-parse: set Ident.value based on initial_facts
	def set_identifiers(self) -> None:
		def visit(e: Expr) -> None:
			if isinstance(e, Ident):
				# True if present in initial facts, else False
				e.value = e.name in self.initial_facts
			elif isinstance(e, Not):
				visit(e.child)
			elif isinstance(e, (And, Or, Xor)):
				for t in e.terms:
					visit(t)

		for r in self.rules:
			visit(r.premise)
			visit(r.conclusion)
