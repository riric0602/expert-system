from parsing.data import And, Or, Not, Xor, Implies, Eqv

def operations(op):
    if isinstance(op, And):
        return op.terms[0] + op.terms[1]
    if isinstance(op, Or):
        return op.terms[0] | op.terms[1]
    if isinstance(op, Xor):
        return op.terms[0] ^ op.terms[1]

def implication(premise, conclusion):
    premise_value = None
    
