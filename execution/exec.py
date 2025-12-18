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


class ContradictionException(Exception):
    pass


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
            if expr.name in visited:
                return expr.value
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
            result = False
            for v in vals:
                if v != None:
                    result ^= v
            return result

        return None
    

    def conclude_ident(self, expr, conclusion_result, ident):
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
                        raise ContradictionException(f"Contradiction detected in rule")
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

        # Known value
        if ident.value is not None:
            return ident.value

        if visited is None:
            visited = set()

        visited.add(ident.name)
        results = []

        if symbol_node.produced_by_rules == [] and ident in self.queries:
            return False

        # Only rules that can produce this fact
        for rn in symbol_node.produced_by_rules:
            rule = rn.rule
            result = None

            if isinstance(rule, Implies):
                premise_value = self.eval_expr(rule.premise, visited)
                conclusion = rule.conclusion
                conclusion_result = None

                if premise_value is True:
                    conclusion_result = True
                elif premise_value is False:
                    conclusion_result = False

            elif isinstance(rule, Equiv):
                if self.ident_in_expr(rule.left, ident):
                    conclusion_result = self.eval_expr(rule.right, visited)
                    conclusion = rule.left
                else:
                    conclusion_result = self.eval_expr(rule.left, visited)
                    conclusion = rule.right

            if conclusion_result is not None:
                result = self.conclude_ident(conclusion, conclusion_result, ident)

            results.append(result)

        # Resolve final value
        determined = [r for r in results if r is not None]

        if len(determined) > 1 and any(r != determined[0] for r in determined):
            raise ContradictionException(f"in rules for {ident.name}")
        
        if True in determined:
            ident.value = True
        elif False in determined:
            ident.value = False
        else:
            ident.value = None

        return ident.value

        
    def update_ident_in_rule(self, ident):
        # Get the symbol node for this ident
        if ident.name not in self.symbol_nodes:
            return
        
        self.symbols[ident.name].value = ident.value
        self.symbol_nodes[ident.name].value = ident.value
        
        symbol_node = self.symbol_nodes[ident.name]
        
        # Update in rules that produce this symbol
        for rn in symbol_node.produced_by_rules:
            rule = rn.rule
            if isinstance(rule, Implies):
                self._update_expr_values(rule.premise, ident)
                self._update_expr_values(rule.conclusion, ident)
            elif isinstance(rule, Equiv):
                self._update_expr_values(rule.left, ident)
                self._update_expr_values(rule.right, ident)
        
        # Update in rules that use this symbol
        for rn in symbol_node.used_in_rules:
            rule = rn.rule
            if isinstance(rule, Implies):
                self._update_expr_values(rule.premise, ident)
                self._update_expr_values(rule.conclusion, ident)
            elif isinstance(rule, Equiv):
                self._update_expr_values(rule.left, ident)
                self._update_expr_values(rule.right, ident)


    def _update_expr_values(self, expr, ident):
        """Helper to update a specific ident in an expression"""
        if isinstance(expr, Ident):
            if expr.name == ident.name:
                expr.value = ident.value
        elif isinstance(expr, Not):
            self._update_expr_values(expr.child, ident)
        elif isinstance(expr, (And, Or, Xor)):
            for t in expr.terms:
                self._update_expr_values(t, ident)
        elif isinstance(expr, Implies):
            self._update_expr_values(expr.premise, ident)
            self._update_expr_values(expr.conclusion, ident)
        elif isinstance(expr, Equiv):
            self._update_expr_values(expr.left, ident)
            self._update_expr_values(expr.right, ident)


    def backward_chaining(self):
        try:
            # Step 1: deduce queries
            for q in self.queries:
                q.value = self.prove(q)
                self.update_ident_in_rule(q)

            # Step 2: deduce all symbols (fill unknowns for non-queries)
            for s in self.symbols.values():
                if s not in self.queries and s.value is None:
                    val = self.prove(s)
                    if val is None:
                        s.value = False
                    else:
                        s.value = val
                    self.update_ident_in_rule(s)

            # Step 3: re-evaluate queries with updated facts
            for q in self.queries:
                if q.value is None:
                    q.value = self.prove(q)
                    self.update_ident_in_rule(q)
        except Exception:
            raise

        return self.queries
