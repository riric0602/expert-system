from parsing.data import *

class Engine:
    def __init__(self, pr: ParseResult):
        self.rules = pr.rules
        self.original_rules = pr.original_rules
        self.symbols = { ident.name: ident for ident in pr.symbols }
        self.queries = pr.queries


    def eval_expr(self, expr, visited):
        if isinstance(expr, Ident):
            return self.prove(expr, visited)
        if isinstance(expr, Not):
            v = self.eval_expr(expr.child, visited)
            return None if v is None else not v
        if isinstance(expr, And):
            vals = [self.eval_expr(t, visited) for t in expr.terms]
            if any(v is False for v in vals):
                return False
            if any(v is None for v in vals):
                return None
            return True
        if isinstance(expr, Or):
            vals = [self.eval_expr(t, visited) for t in expr.terms]
            if any(v is True for v in vals):
                return True
            if all(v is False for v in vals):
                return False
            return None
        if isinstance(expr, Xor):
            l = self.eval_expr(expr.terms[0], visited)
            r = self.eval_expr(expr.terms[1], visited)
            if l is None or r is None:
                return None
            return (l and not r) or (r and not l)
        return None


    def ident_in_expr(self, expr: Expr, goal: Ident):
        if isinstance(expr, Ident):
            return expr.name == goal.name
        if isinstance(expr, (And, Or, Xor)):
            return any(self.ident_in_expr(t, goal) for t in expr.terms)
        return False


    def idents_in_expr(self, expr):
        if isinstance(expr, Ident):
            return [expr]
        if isinstance(expr, Not):
            return self.idents_in_expr(expr.child)
        if isinstance(expr, (And, Or, Xor)):
            ids = []
            for t in expr.terms:
                ids.extend(self.idents_in_expr(t))
            return ids
        return []


    def prove(self, goal: Ident, visited=None):
        ident = self.symbols[goal.name]

        if ident.value is not None:
            return ident.value

        if visited is None:
            visited = set()
        if ident.name in visited:
            return None
        visited.add(ident.name)

        rule_results = []

        for rule, original_rule in zip(self.rules, self.original_rules):
            conclusions = []

            # Collect all relevant Idents for this goal
            if isinstance(rule, Implies):
                for i in self.idents_in_expr(rule.conclusion):
                    if i.name == ident.name:
                        conclusions.append(i)
            elif isinstance(rule, Equiv):
                for side in [rule.left, rule.right]:
                    if self.ident_in_expr(side, ident):
                        conclusions.append(side)

            if not conclusions:
                continue

            # Evaluate premise
            premise_value = None
            if isinstance(rule, Implies):
                premise_value = self.eval_expr(rule.premise, visited)
            elif isinstance(rule, Equiv):
                left_val = self.eval_expr(rule.left, visited)
                right_val = self.eval_expr(rule.right, visited)
                if left_val is None or right_val is None:
                    premise_value = None
                else:
                    premise_value = left_val == right_val

            # Set result for each conclusion ident
            for c in conclusions:
                result = True if premise_value else None
                self.symbols[c.name].value = result
                rule_results.append(result)

                # LOGS: keep your resolution prints exactly
                idents = list({i.name: i for i in self.idents_in_expr(c)}.values())
                print(f"We know that :")
                for i in idents:
                    print(f"{i.name} is {i.value}")
                print("---------------------------------------------------------")
                print("Conclusion") 
                print("---------------------------------------------------------")
                print(f"Since we know {original_rule}, then {ident.name} is {result}")

        # Resolve final value for goal
        determined = [v for v in rule_results if v is not None]
        if len(determined) > 1 and any(v != determined[0] for v in determined):
            raise ValueError(f"Contradiction in rule conclusions for {goal.name}")

        if True in determined:
            ident.value = True
        elif False in determined:
            ident.value = False
        else:
            ident.value = None
        return ident.value


    def backward_chaining(self):
        for q in self.queries:
            print("---------------------------------------------------------")
            print(f"Proving {q.name} : {q.value}")
            print("---------------------------------------------------------")
            q.value = self.prove(q)
        return self.queries
