from dataclasses import dataclass
from typing import List, Set, Union

# Expr nodes
class Expr: pass

@dataclass
class Ident(Expr):
	name: str	# 'A'-'Z'

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
