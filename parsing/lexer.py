#!/usr/bin/env python3

import re
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Token:
	type: str
	value: Optional[str]
	index: int

# Token labels correspondance
# One big regex with named groups
TOKEN_REGEX = re.compile(
	r"""
		(?P<EQUIV><=>)         |  # equivalence
		(?P<IMPLIES>=\>)       |  # implication
		(?P<LPAREN>\()         |  # (
		(?P<RPAREN>\))         |  # )
		(?P<NOT>!)             |  # !
		(?P<AND>\+)            |  # +
		(?P<OR>\|)             |  # |
		(?P<XOR>[ˆ^])          |  # XOR: accepts U+02C6 (ˆ) or ASCII ^
		(?P<IDENT>[A-Z]+)      |  # identifiers from A-Z
		(?P<WS>\s+)               # whitespaces
	""",
	re.VERBOSE,
)

def tokenize(text: str) -> List[Token]:
	tokens: List[Token] = []

	i = 0
	while i < len(text):
		# Check for regex match
		m = TOKEN_REGEX.match(text, i)

		# Syntax error, no matches found
		if not m:
			# Unknown character, syntax error with context
			wrong_char = text[i]
			neighbor_text = text[max(0, i-10):i+10]
			raise ValueError(f"Unknown character {wrong_char!r} at index {i}. Context: {neighbor_text!r}")
		
		# Get value and type of token
		token_type = m.lastgroup
		value = m.group(token_type)

		# Skips white spaces
		if token_type == "WS":
			i = m.end()
			continue
		
		# Add token to the list
		tokens.append(Token(token_type, value if token_type in {"IDENT"} else None, m.start()))
		i = m.end()
	return tokens
