from execution.exec import Engine, ContradictionException
from parsing.file_utils import parser
import sys

def run(file_path):
    pr = parser(file_path)

    print(pr)

    engine = Engine(pr)
    results = engine.backward_chaining()
    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]

    try:
        results = run(file_path)
        # Print results nicely for CLI
        print("Query results:")
        for q in results:
            print(f"  {q.name}: {q.value}")
    except ContradictionException as e:
        print(f"Contradiction detected: {e}")
        sys.exit(1)
