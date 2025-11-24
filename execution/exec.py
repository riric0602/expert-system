from parsing.data import *
from parsing.parser import pretty_rule
from .operations import eval_expr

def conclusion_contains(expr, goal):
    """Check if the conclusion expression contains the query."""
    if isinstance(expr, Ident):
        return expr.name == goal.name

    if isinstance(expr, (And, Or, Xor)):
        return any(conclusion_contains(t, goal) for t in expr.terms)

    return False


def idents_in_premise(expr):
    if isinstance(expr, Ident):
        print([expr])
        return [expr]

    if isinstance(expr, Not):
        return idents_in_premise(expr.child)

    if isinstance(expr, (And, Or, Xor)):
        ids = []
        for t in expr.terms:
            ids.extend(idents_in_premise(t))
        return ids

    return []


def prove(goal: Ident, pr: ParseResult, visited=None):
    """Prove the value of a query using backward chaining."""
    print("---------------------------------------------------------")
    if visited is None:
        visited = set()

    print("Visited: ", visited)

    name = goal.name

    print(f"value of {name}: {goal.value}")

    # If the goal value is already set, return it
    if goal.value is not None:
        return goal.value
    
    visited.add(name)

    found_rule = False
    rule_results = []

    # search for rules whose conclusion contains this goal
    for rule in pr.rules:

        if conclusion_contains(rule.conclusion, goal):
            found_rule = True
            v = eval_expr(rule.premise, pr, visited)

            idents = list(
                {i.name: i for i in idents_in_premise(rule.premise)}
                .values()
                )
            print(f"We know that :")
            for i in idents:
                print(f"{i.name} is {i.value}")
        
            print("---------------------------------------------------------")
            print("Conclusion") 
            print("---------------------------------------------------------")
            # only for implies
            if v is False:
                print(f"Since {pretty_rule(rule)} is False, then {name} is Undetermined")
                v = None

            else:
                print(f"Since {pretty_rule(rule)} is True, then {name} is True")
            
            rule_results.append(v)
    
    if found_rule is False:
        print(f"No rule with {name} was found in conclusion, then it stays Undetermined")
        return None
    
    # if all conclusions lead to different values => contradictions
    # Filter out undetermined results
    determined = [v for v in rule_results if v is not None]

    # If there are multiple determined results that disagree, it's a contradiction
    if len(determined) > 1 and any(v != determined[0] for v in determined):
        raise ValueError("Contradiction in rule conclusions. Fix logic.")

    # If at least one rule proves it True → return True
    if True in determined:
        return True

    # If no rule proves it → keep undetermined
    return None


def backward_chaining(pr: ParseResult):
    try:
        for q in pr.queries:
            print("Proving E")
            q.value = prove(q, pr)
            print(f"{q.name} : {q.value}")
            print("---------------------------------------------------------")
    except Exception as e:
        print("Error: ", e)
        exit()
        