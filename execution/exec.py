from parsing.data import *
from parsing.parser import pretty_rule
from .operations import eval_expr


def conclusion_contains(expr: Expr, goal: Ident):
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
    found_rule = False
    rule_results = []
    name = goal.name
    result = goal.value

    if goal.value is not None:
        return goal.value, pr
    
    if visited is None:
        visited = set()

    visited.add(name)
    print("Visited: ", visited)

    # search for rules whose conclusion contains this goal
    for rule, original_rule in zip(pr.rules, pr.original_rules):
        if conclusion_contains(rule.conclusion, goal):
            found_rule = True
            result = eval_expr(rule.premise, pr, visited)

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
            if result is False:
                result = None
            else:
                result = True
            
            print(f"Since we know {original_rule}, then {name} is {result}")
            rule_results.append(result)
    
    if found_rule is False:
        print(f"No rule with {name} was found in conclusion, then it stays Undetermined")
        result = None
    
    # if all conclusions lead to different values => contradictions
    determined = [v for v in rule_results if v is not None]

    # If there are multiple determined results that disagree, it's a contradiction
    if len(determined) > 1 and any(v != determined[0] for v in determined):
        raise ValueError("Contradiction in rule conclusions. Fix logic.")

    if True in determined:
        result = True

    return result


def backward_chaining(pr: ParseResult):
    try:
        for q in pr.queries:
            print(f"Proving {q.name}")
            q.value = prove(q, pr)
            print(f"{q.name} : {q.value}")
            print("---------------------------------------------------------")
    except Exception as e:
        print("Error: ", e)
        exit()
        