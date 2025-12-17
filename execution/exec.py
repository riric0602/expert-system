from parsing.data import *

class SymbolNode:
    def __init__(self, ident):
        self.ident = ident
        self.produced_by_rules = []
        self.used_in_rules = []


class RuleNode:
    def __init__(self, rule, original):
        self.rule = rule
        self.original = original
        self.premise_idents = []
        self.conclusion_idents = []

class Engine:
    def __init__(self, pr: ParseResult):
        self.rules = pr.rules
        self.original_rules = pr.original_rules
        self.symbols = {ident.name: ident for ident in pr.symbols}
        self.queries = pr.queries

        self.symbol_nodes = {}
        self.rule_nodes = []

        self.build_graph()

    # --------------------------------------------------
    # Graph construction
    # --------------------------------------------------

    def build_graph(self):
        # Create fact nodes
        for ident in self.symbols.values():
            self.symbol_nodes[ident.name] = SymbolNode(ident)

        # Create rule nodes and link graph
        for rule, original in zip(self.rules, self.original_rules):
            rn = RuleNode(rule, original)

            if isinstance(rule, Implies):
                rn.premise_idents = self.idents_in_expr(rule.premise)
                rn.conclusion_idents = self.idents_in_expr(rule.conclusion)

            elif isinstance(rule, Equiv):
                rn.premise_idents = (
                    self.idents_in_expr(rule.left)
                    + self.idents_in_expr(rule.right)
                )
                rn.conclusion_idents = rn.premise_idents

            self.rule_nodes.append(rn)

            for i in rn.premise_idents:
                self.symbol_nodes[i.name].used_in_rules.append(rn)

            for i in rn.conclusion_idents:
                self.symbol_nodes[i.name].produced_by_rules.append(rn)

    # --------------------------------------------------
    # Utils
    # --------------------------------------------------

    def is_not_query(self, ident: Ident) -> bool:
        return ident.value is not True and ident.name not in [q.name for q in self.queries]


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

    # --------------------------------------------------
    # Propositional Logic
    # --------------------------------------------------

    def eval_expr(self, expr, visited):
        if isinstance(expr, Ident):
            value = self.prove(expr, visited)
            return value

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
            vals = [self.eval_expr(t, visited) for t in expr.terms]
            if any(v is None for v in vals):
                return None
            result = False
            for v in vals:
                result ^= v
            return result

        return None
    

    def conclude_ident(self, expr, conclusion_result, ident, visited):
        terms = expr.terms if hasattr(expr, "terms") else [expr]

        # Peek helper: observe without proving / defaulting
        def peek(expr):
            if isinstance(expr, Ident):
                return expr.value

            if isinstance(expr, Not):
                v = peek(expr.child)
                return None if v is None else not v

            if isinstance(expr, And):
                vals = [peek(t) for t in expr.terms]
                if any(v is False for v in vals):
                    return False
                if any(v is None for v in vals):
                    return None
                return True

            if isinstance(expr, Or):
                vals = [peek(t) for t in expr.terms]
                if any(v is True for v in vals):
                    return True
                if all(v is False for v in vals):
                    return False
                return None

            if isinstance(expr, Xor):
                vals = [peek(t) for t in expr.terms]
                if any(v is None for v in vals):
                    return None
                result = False
                for v in vals:
                    result ^= v
                return result

            return None

        # ---------------- Ident ----------------
        if isinstance(expr, Ident):
            return conclusion_result

        # ---------------- AND ----------------
        if isinstance(expr, And):
            if conclusion_result is True:
                # contradiction if any other term known false
                for t in terms:
                    if isinstance(t, Ident) and t.name == ident.name:
                        continue
                    if peek(t) is False:
                        raise ValueError("Contradiction in AND conclusion")
                return True

            if conclusion_result is False:
                # if all others known true → query must be false
                all_true = True
                for t in terms:
                    if isinstance(t, Ident) and t.name == ident.name:
                        continue
                    if peek(t) is not True:
                        all_true = False
                        break
                return False if all_true else None

            return None

        # ---------------- OR ----------------
        if isinstance(expr, Or):
            if conclusion_result is False:
                return False

            if conclusion_result is True:
                # if all others known false → query true
                all_false = True
                for t in terms:
                    if isinstance(t, Ident) and t.name == ident.name:
                        continue
                    if peek(t) is not False:
                        all_false = False
                        break
                return True if all_false else None

            return None

        # ---------------- XOR ----------------
        if isinstance(expr, Xor):
            true_count = 0
            unknown = False

            for t in terms:
                if isinstance(t, Ident) and t.name == ident.name:
                    continue
                v = peek(t)
                if v is True:
                    true_count += 1
                elif v is None:
                    unknown = True

            if conclusion_result is True:
                if true_count == 0 and not unknown:
                    return True
                if true_count >= 1:
                    return False
                return None

            if conclusion_result is False:
                if true_count == 1:
                    return True
                if true_count == 0 and not unknown:
                    return False
                return None

        # ---------------- NOT ----------------
        if isinstance(expr, Not):
            return None if conclusion_result is None else not conclusion_result

        return None


    
    # --------------------------------------------------
    # Backward chaining over the graph
    # --------------------------------------------------

    def prove(self, goal: Ident, visited=None):
        symbol_node = self.symbol_nodes[goal.name]
        ident = symbol_node.ident
        is_false_fact = self.is_not_query(ident)

        # Known value
        if ident.value is not None:
            return ident.value

        if visited is None:
            visited = set()

        # Cycle detected
        if ident.name in visited:
            return False if is_false_fact else None

        visited.add(ident.name)
        results = []

        # Only rules that can produce this fact
        for rn in symbol_node.produced_by_rules:
            rule = rn.rule
            print(rn.original)
            result = None

            if isinstance(rule, Implies):
                premise_value = self.eval_expr(rule.premise, visited)
                conclusion = rule.conclusion

                if premise_value is True:
                    conclusion_result = True
                else:
                    conclusion_result = None

            elif isinstance(rule, Equiv):
                if self.ident_in_expr(rule.left, ident):
                    conclusion_result = self.eval_expr(rule.right, visited)
                    conclusion = rule.left
                else:
                    conclusion_result = self.eval_expr(rule.left, visited)
                    conclusion = rule.right

            if conclusion_result != None:
                result = self.conclude_ident(conclusion, conclusion_result, ident, visited)
            else:
                result = None

            results.append(result)

            # ---- Reasoning log ----
            # print("---------------------------------------------------------")
            # print(f"Applied rule: {rn.original}")
            # print(f"Goal {ident.name} deduced as {result}")
            # print("---------------------------------------------------------")

        # Resolve final value
        determined = [r for r in results if r is not None]

        if len(determined) > 1 and any(r != determined[0] for r in determined):
            raise ValueError(f"Contradiction in rules for {ident.name}")

        if True in determined:
            ident.value = True
        else:
            ident.value = False

        print(f"{ident.name}: {ident.value}")
        return ident.value


    def backward_chaining(self):
        try:
            for q in self.queries:
                # print("=========================================================")
                # print(f"Proving {q.name}")
                # print("=========================================================")
                q.value = self.prove(q)
                # print(f"Final deduced value: {q.name} = {q.value}\n")
        except ValueError as e:
            print("Error:", e)
            exit(1)

        return self.queries
