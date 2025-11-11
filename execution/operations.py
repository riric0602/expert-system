from parsing.data import And, Or, Not, Xor, Implies, Eqv, Ident

def eval_expr(expr, pr, known, visited):
    """Recursively evaluate logical expressions in backward chaining."""
    from .exec import prove

    if isinstance(expr, Ident):
        if expr.name in known:
            return True
        return prove(expr, pr, known, visited)

    if isinstance(expr, And):
        return all(eval_expr(term, pr, known, visited.copy()) for term in expr.terms)

    if isinstance(expr, Or):
        return any(eval_expr(term, pr, known, visited.copy()) for term in expr.terms)

    if isinstance(expr, Not):
        return not eval_expr(expr.child, pr, known, visited.copy())

    if isinstance(expr, Xor):
        vals = [eval_expr(term, pr, known, visited.copy()) for term in expr.terms]
        return vals[0] ^ vals[1]

    return False
    
