from parsing.data import *

def eval_expr(expr, pr, visited):
    """Evaluate a logical expression using backward chaining."""
    from .exec import prove

    # Direct match
    if isinstance(expr, Ident):
        return prove(expr, pr, visited)

    # NOT
    if isinstance(expr, Not):
        v = eval_expr(expr.child, pr, visited.copy())
        if v is None:
            return None
        return not v

    # AND
    if isinstance(expr, And):
        values = []
        for t in expr.terms:
            v = eval_expr(t, pr, visited.copy())
            values.append(v)
            if v is False:
                return False      # AND short-circuit
        # if any is None → undetermined
        if any(v is None for v in values):
            return None
        return True               # all true

    # OR
    if isinstance(expr, Or):
        values = []
        for t in expr.terms:
            v = eval_expr(t, pr, visited.copy())
            values.append(v)
            if v is True:
                return True       # OR short-circuit
        # if all false → false
        if all(v is False for v in values):
            return False
        return None               # mixed false/None

    # XOR (binary only)
    if isinstance(expr, Xor):
        left, right = expr.terms
        l = eval_expr(left, pr, visited.copy())
        r = eval_expr(right, pr, visited.copy())

        # If either is undetermined → undetermined
        if l is None or r is None:
            return None

        # XOR truth table
        return (l and not r) or (r and not l)

    # unknown expression node
    return None
