from parsing.data import *
from .operations import eval_expr

def conclusion_contains(expr, goal):
    """Check if the conclusion expression contains the query."""
    if isinstance(expr, Ident):
        return expr.name == goal.name

    if isinstance(expr, (And, Or, Xor)):
        return any(conclusion_contains(t, goal) for t in expr.terms)

    return False

def prove(goal: Ident, pr: ParseResult, visited=None):
    """Prove the value of a query using backward chaining."""
    if visited is None:
        visited = set()

    name = goal.name

    # If the goal value was already set earlier, return it
    if goal.value is not None:
        return goal.value
    
    # Detect cycle and value proven undetermined
    if name in visited:
        return UNDETERMINED
    
    visited.add(name)

    found_rule = False
    rule_results = []

    # search for rules whose conclusion contains this goal
    for rule in pr.rules:
        if conclusion_contains(rule.conclusion, goal):
            found_rule = True
            v = eval_expr(rule.premise, pr, visited.copy())
            rule_results.append(v)

    # no rules lead to this goal → false
    if not found_rule:
        return UNDETERMINED
    
    # if any rule proves it true → true
    if any(v is TRUE for v in rule_results):
        return TRUE

    # if all rules are false → false
    if all(v is FALSE for v in rule_results):
        return FALSE

    # mixed → undetermined
    return UNDETERMINED

def backward_chaining(pr: ParseResult):
    for q in pr.queries:
        q.value = prove(q, pr)
