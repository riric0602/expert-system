from parsing.data import And, Or, Not, Xor, Ident

def eval_prop(expr, pr, visited):
    """Recursively evaluate logical expressions in backward chaining."""
    from .exec import prove

    if isinstance(expr, Ident):
        if expr.name in pr.initial_facts:
            return True
        return prove(expr, pr, visited)

    if isinstance(expr, And):
        return all(
            eval_prop(term, pr, visited.copy()) for term in expr.terms
        )

    if isinstance(expr, Or):
        return any(
            eval_prop(term, pr, visited.copy()) for term in expr.terms
        )

    if isinstance(expr, Not):
        return not eval_prop(expr.child, pr, visited.copy())

    if isinstance(expr, Xor):
        vals = [eval_prop(term, pr, visited.copy()) for term in expr.terms]
        return vals[0] ^ vals[1]

    return False
    
