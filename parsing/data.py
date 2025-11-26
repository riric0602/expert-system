from dataclasses import dataclass
from typing import List, Set, Union, Optional

# Expr nodes
class Expr: pass

@dataclass
class Ident(Expr):
	name: str	# 'A'-'Z'
	value: Optional[bool] = None

	def __hash__(self) -> int:
		# Hash only by name so instances with same name dedupe in sets
		return hash(self.name)

	def __eq__(self, other: object) -> bool:
		return isinstance(other, Ident) and self.name == other.name

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
class Equiv:
    left: Expr
    right: Expr

# Parsing result
@dataclass
class ParseResult:
	rules: List[Union[Implies, Equiv]]
	initial_facts: Set[str]
	queries: List[Ident]
	symbols: Set[Ident]
	original_rules: List[str]

	# Post-parse: set Ident.value based on initial_facts
	def set_identifiers(self) -> None:
		query_names = {q.name for q in self.queries}

		def visit(e: Expr) -> None:
			if isinstance(e, Ident):
				# True if present in initial facts.
				# If it's a queried symbol and not in facts, keep None instead of False.
				if e.name in self.initial_facts:
					e.value = True
				elif e.name in query_names:
					e.value = None
				else:
					e.value = False
			elif isinstance(e, Not):
				visit(e.child)
			elif isinstance(e, (And, Or, Xor)):
				for t in e.terms:
					visit(t)

		# Update identifiers within rules
		for r in self.rules:
			if isinstance(r, Implies):
				visit(r.premise)
				visit(r.conclusion)
			else:  # Equiv
				visit(r.left)
				visit(r.right)

		# For queries and symbols, keep None when not in initial facts
		for q in self.queries:
			if q.name in self.initial_facts:
				q.value = True
		for s in self.symbols:
			if s.name in self.initial_facts:
				s.value = True
