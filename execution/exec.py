from parsing.data import *

class Engine:
    def __init__(self, pr: ParseResult):
        self.rules = pr.rules
        self.original_rules = pr.original_rules
        self.symbols = {ident.name: ident for ident in pr.symbols}
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
        if isinstance(expr, Implies):
            return self.idents_in_expr(expr.premise) + self.idents_in_expr(expr.conclusion)
        if isinstance(expr, Equiv):
            return self.idents_in_expr(expr.left) + self.idents_in_expr(expr.right)
        return []


    def ident_in_expr(self, expr, goal):
        return any(i.name == goal.name for i in self.idents_in_expr(expr))


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
            goal_in_rule = False
            if isinstance(rule, Implies):
                goal_in_rule = self.ident_in_expr(rule.conclusion, ident)
            elif isinstance(rule, Equiv):
                goal_in_rule = self.ident_in_expr(rule.left, ident) or self.ident_in_expr(rule.right, ident)
            if not goal_in_rule:
                continue

            # Evaluate premise or sides
            premise_value = None
            if isinstance(rule, Implies):
                premise_value = self.eval_expr(rule.premise, visited)
            elif isinstance(rule, Equiv):
                if self.ident_in_expr(rule.left, ident):
                    premise_value = self.eval_expr(rule.right, visited)
                elif self.ident_in_expr(rule.right, ident):
                    premise_value = self.eval_expr(rule.left, visited)
                else:
                    premise_value = None

            # Deduce goal value
            result = None
            if premise_value is not None:
                # For Implies: True premise → conclusion true
                if isinstance(rule, Implies):
                    if self.ident_in_expr(rule.conclusion, ident):
                        if isinstance(rule.conclusion, Ident):
                            if premise_value is True:
                                result = True
                            else:
                                result = None
                        else:
                            result = self.eval_expr(rule.conclusion, visited)
                        if premise_value is True and result is False:
                            raise ValueError(f"Contradiction in rule: {original_rule}")
                elif isinstance(rule, Equiv):
                    result = premise_value

            rule_results.append(result)

            # --- Reasoning log ---
            print("---------------------------------------------------------")
            if isinstance(rule, Implies):
                print("Premise:")
                for t in self.idents_in_expr(rule.premise):
                    print(f"  {t.name} = {t.value}")
                print(f"Applied rule: {original_rule}")
            elif isinstance(rule, Equiv):
                print("Equivalence:")
                goal_side = "Left" if self.ident_in_expr(rule.left, ident) else "Right"
                print(f"Goal {ident.name} is on {goal_side} side")
            print(f"Goal {ident.name} deduced as {result}")
            print("---------------------------------------------------------")

        # Resolve final value
        determined = [v for v in rule_results if v is not None]
        if len(determined) > 1 and any(v != determined[0] for v in determined):
            raise ValueError(f"Contradiction in rules for {goal.name}")
        if True in determined:
            ident.value = True
        elif False in determined:
            ident.value = False
        else:
            ident.value = None
        return ident.value


    def backward_chaining(self):
        for q in self.queries:
            print("=========================================================")
            print(f"Proving {q.name} : {q.value}")
            print("=========================================================")
            q.value = self.prove(q)
            print(f"Final deduced value: {q.name} = {q.value}\n")
        return self.queries
