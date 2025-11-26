from parsing.data import *


class Engine:
    def __init__(self, pr: ParseResult):
        self.pr = pr
        self.symbols = {}
        self._normalize()


    def _normalize(self):
        """Create a shared Ident instance for every identifier and rewrite rules/queries."""
        self.symbols = { ident.name: ident for ident in self.pr.symbols }

        def replace(expr):
            if isinstance(expr, Ident):
                return self.symbols[expr.name]

            if isinstance(expr, Not):
                expr.child = replace(expr.child)
                return expr

            if isinstance(expr, (And, Or, Xor)):
                expr.terms = [replace(t) for t in expr.terms]
                return expr

            if isinstance(expr, Implies):
                expr.premise = replace(expr.premise)
                expr.conclusion = replace(expr.conclusion)
                return expr

            if isinstance(expr, Equiv):
                expr.left = replace(expr.left)
                expr.right = replace(expr.right)
                return expr

            return expr

        for r in self.pr.rules:
            replace(r)

        # force queries to use shared objects
        for i, q in enumerate(self.pr.queries):
            self.symbols[q.name] = self.pr.queries[i]


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
        """Check if the conclusion expression contains the query."""
        if isinstance(expr, Ident):
            return expr.name == goal.name

        if isinstance(expr, (And, Or, Xor)):
            return any(self.ident_in_expr(t, goal) for t in expr.terms)

        return False


    def idents_in_premise(self, expr):
        if isinstance(expr, Ident):
            return [expr]

        if isinstance(expr, Not):
            return self.idents_in_premise(expr.child)

        if isinstance(expr, (And, Or, Xor)):
            ids = []
            for t in expr.terms:
                ids.extend(self.idents_in_premise(t))
            return ids

        return []


    # Backchaining Algorithm Functions
    def prove(self, goal: Ident, visited=None):
        ident = self.symbols[goal.name]

        if ident.value is not None:
            return ident.value

        if visited is None:
            visited = set()
        if ident.name in visited:
            return None
        visited.add(ident.name)

        print("Visited: ", visited)

        found_rule = False
        rule_results = []
        result = None

        for rule, original_rule in zip(self.pr.rules, self.pr.original_rules):
            if isinstance(rule, Implies):
                if self.ident_in_expr(rule.conclusion, ident):
                    found_rule = True
                    premise_value = self.eval_expr(rule.premise, visited)
                    result = True if premise_value is not False else None

                    rule_results.append(result)

                    # Reasolution prints
                    idents = list(
                        {i.name: i for i in self.idents_in_premise(rule.premise)}
                        .values()
                    )
                    
                    print(f"We know that :")
                    for i in idents:
                        print(f"{i.name} is {i.value}")

                    print("---------------------------------------------------------")
                    print("Conclusion") 
                    print("---------------------------------------------------------")

                    print(f"Since we know {original_rule}, then {ident.name} is {result}")

            elif isinstance(rule, Equiv):
                if self.ident_in_expr(rule.left, ident):
                    found_rule = True
                    right_value = self.eval_expr(rule.right, visited)

                    if right_value:
                        result = True
                    else:
                        result = False

                    rule_results.append(result)

                    # Reasolution prints
                    idents = list(
                        {i.name: i for i in self.idents_in_premise(rule.right)}
                        .values()
                    )
                    
                    print(f"We know that :")
                    for i in idents:
                        print(f"{i.name} is {i.value}")

                    print("---------------------------------------------------------")
                    print("Conclusion") 
                    print("---------------------------------------------------------")

                    print(f"Since we know {original_rule}, then {ident.name} is {result}")

                elif self.ident_in_expr(rule.right, ident):
                    found_rule = True
                    left_value = self.eval_expr(rule.left, visited)

                    if left_value:
                        result = True
                    else:
                        result = False

                    rule_results.append(result)

                    # Reasolution prints
                    idents = list(
                        {i.name: i for i in self.idents_in_premise(rule.left)}
                        .values()
                    )
                    
                    print(f"We know that :")
                    for i in idents:
                        print(f"{i.name} is {i.value}")

                    print("---------------------------------------------------------")
                    print("Conclusion") 
                    print("---------------------------------------------------------")

                    print(f"Since we know {original_rule}, then {ident.name} is {result}")
        
        if not found_rule:
            ident.value = None
            return None

        determined = [v for v in rule_results if v is not None]
        if len(determined) > 1 and any(v != determined[0] for v in determined):
            raise ValueError("Contradiction in rule conclusions. Fix logic.")

        if True in determined:
            result = True
        elif False in determined:
            result = False
        else:
            result = None

        ident.value = result
        return result

    
    def backward_chaining(self):
        try:
            for q in self.pr.queries:
                print("---------------------------------------------------------")
                print(f"Proving {q.name} : {q.value}")
                if q.value == None:
                    q.value = self.prove(goal=q)
        except Exception as e:
            print("Error: ", e)
            exit()
