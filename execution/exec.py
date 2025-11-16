from parsing.data import ParseResult, Ident, Eqv, Implies, And, Or, Not, Xor
from .operations import eval_expr

def prove(goal: Ident, pr: ParseResult, visited=None):
    """Try to prove a goal identifier using backward chaining."""
    known = pr.initial_facts

    if visited is None:
        visited = set()

    # avoid re-proving the same goal
    if goal.name in visited:
        return False
    visited.add(goal.name)

    # if fact, return true
    if goal.name in known:
        return True

    # find all rules that can produce this goal
    for rule in pr.rules:
        if isinstance(rule.conclusion, Ident):
            # direct match
            if rule.conclusion.name == goal.name:
                if eval_expr(rule.premise, pr, visited.copy()):
                    known.add(goal.name)
                    return True

        elif isinstance(rule.conclusion, And):
            for sub in rule.conclusion.terms:
                if sub.name == goal.name:
                    if eval_expr(rule.premise, pr, visited.copy()):
                        known.add(goal.name)
                        return True

    return False


def backward_chaining(pr: ParseResult):
    for q in pr.queries:
        q.value = prove(q, pr)

    print("Results:")
    for q in pr.queries:
        print(f"{q.name}: {'True' if q.value else 'False'}")
