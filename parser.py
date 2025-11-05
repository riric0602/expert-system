#!/usr/bin/env python3

import sys
from pathlib import Path
from typing import Tuple

def check_file(filepath : str) -> Tuple [bool, bool]:
	p = Path(filepath)
	if not p.is_file():
		return (False, False)
	return (True, p.stat().st_size == 0)


def main():
	# Only one argument
	if len(sys.argv) != 2:
		print(f"Usage: {sys.argv[0]} <path/to/file>")
		sys.exit(1)

	# File exists and has content
	path = sys.argv[1]
	print(path)

	file_check = check_file()
	if (file_check.__contains__(False)):
		print(f"File does not exist or is empty")
		sys.exit(1)
	
	


if __name__ == "__main__":
	main()