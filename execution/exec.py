from parsing.data import ParseResult, Ident, Eqv, Implies
from .operations import *

def ident_in_rule(ident, rule):
    if isinstance(rule.premise, Ident):
        i = rule.premise
        if i.name == ident.name and i.value == ident.value:
            return True
    if isinstance(rule.conclusion, Ident):
        i = rule.conclusion
        if i.name == ident.name and i.value == ident.value:
            return True
    return False

def execute_rule(rule):
    if isinstance(rule, Implies):
        implication(rule)
        

def prove(q, pr):
    return True


def backward_chaining(pr: ParseResult):
    for q in pr.queries:
        q.value = prove(q, pr)

    print(pr.queries)