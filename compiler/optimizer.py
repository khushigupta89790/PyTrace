
import ast
import operator


class ConstantFolder(ast.NodeTransformer):
    """Evaluate expressions containing constant values."""

    OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow
    }

    UNARY_OPERATORS = {
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
        ast.Not: operator.not_,
        ast.Invert: operator.invert
    }

    def __init__(self):
        self.optimizations = []

    def visit_BinOp(self, node):
        node = self.generic_visit(node)

        if (
            isinstance(node.left, ast.Constant)
            and isinstance(node.right, ast.Constant)
        ):

            operation = self.OPERATORS.get(type(node.op))

            if operation is None:
                return node

            try:
                result = operation(
                    node.left.value,
                    node.right.value
                )

                if isinstance(result, (int, float, str, bool)):
                    self.optimizations.append({
                        "type": "Constant Folding",
                        "original": ast.unparse(node),
                        "optimized": repr(result),
                        "explanation": (
                            "Evaluated an expression containing "
                            "constant values."
                        )
                    })

                    return ast.copy_location(
                        ast.Constant(value=result),
                        node
                    )

            except (
                ArithmeticError,
                TypeError,
                ValueError,
                OverflowError
            ):
                return node

        return node

    def visit_UnaryOp(self, node):
        node = self.generic_visit(node)

        if isinstance(node.operand, ast.Constant):

            operation = self.UNARY_OPERATORS.get(type(node.op))

            if operation is None:
                return node

            try:
                result = operation(node.operand.value)

                if isinstance(result, (int, float, str, bool)):
                    self.optimizations.append({
                        "type": "Constant Folding",
                        "original": ast.unparse(node),
                        "optimized": repr(result),
                        "explanation": (
                            "Evaluated a unary operation containing "
                            "a constant value."
                        )
                    })

                    return ast.copy_location(
                        ast.Constant(value=result),
                        node
                    )

            except (
                ArithmeticError,
                TypeError,
                ValueError,
                OverflowError
            ):
                return node

        return node


class ConstantPropagator(ast.NodeTransformer):
    """
    Propagate constants only through safe, straight-line
    top-level statements.
    """

    def __init__(self):
        self.constants = {}
        self.optimizations = []

    def visit_Module(self, node):
        new_body = []

        for statement in node.body:

            # Avoid propagation through complex scopes
            # and control-flow structures.
            if isinstance(
                statement,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                    ast.ClassDef,
                    ast.If,
                    ast.For,
                    ast.AsyncFor,
                    ast.While,
                    ast.Try,
                    ast.With,
                    ast.AsyncWith,
                    ast.Match
                )
            ):
                self.constants.clear()
                new_body.append(statement)
                continue

            statement = self.visit(statement)
            new_body.append(statement)

        node.body = new_body
        return node

    def visit_Assign(self, node):
        node.value = self.visit(node.value)

        # A function call may modify program state.
        if any(
            isinstance(item, ast.Call)
            for item in ast.walk(node.value)
        ):
            self.constants.clear()

        if (
            len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
        ):

            name = node.targets[0].id

            if isinstance(node.value, ast.Constant):
                self.constants[name] = node.value.value
            else:
                self.constants.pop(name, None)

        else:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.constants.pop(target.id, None)

        return node

    def visit_AugAssign(self, node):

        if isinstance(node.target, ast.Name):
            self.constants.pop(node.target.id, None)

        node.value = self.visit(node.value)
        return node

    def visit_Expr(self, node):
        node.value = self.visit(node.value)

        # Invalidate tracked constants after function calls.
        if any(
            isinstance(item, ast.Call)
            for item in ast.walk(node.value)
        ):
            self.constants.clear()

        return node

    def visit_Name(self, node):

        if (
            isinstance(node.ctx, ast.Load)
            and node.id in self.constants
        ):

            value = self.constants[node.id]

            self.optimizations.append({
                "type": "Constant Propagation",
                "original": node.id,
                "optimized": repr(value),
                "explanation": (
                    f"Replaced '{node.id}' with its known "
                    "constant value."
                )
            })

            return ast.copy_location(
                ast.Constant(value=value),
                node
            )

        return node


class DeadCodeEliminator:
    """Remove unused simple top-level variable assignments."""

    def __init__(self):
        self.optimizations = []

    def eliminate(self, syntax_tree):

        used_variables = set()

        # Collect variable references throughout the AST.
        for node in ast.walk(syntax_tree):

            if (
                isinstance(node, ast.Name)
                and isinstance(node.ctx, ast.Load)
            ):
                used_variables.add(node.id)

            elif isinstance(node, ast.AugAssign):

                if isinstance(node.target, ast.Name):
                    used_variables.add(node.target.id)

        new_body = []

        for node in syntax_tree.body:

            if (
                isinstance(node, ast.Assign)
                and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id not in used_variables
                and isinstance(
                    node.value,
                    (ast.Constant, ast.Name)
                )
            ):

                variable_name = node.targets[0].id

                self.optimizations.append({
                    "type": "Dead Code Elimination",
                    "original": ast.unparse(node),
                    "optimized": "Removed",
                    "explanation": (
                        f"Removed unused variable '{variable_name}'."
                    )
                })

            else:
                new_body.append(node)

        syntax_tree.body = new_body
        return syntax_tree


def optimize_code(source_code):
    """Perform constant folding, propagation and dead code elimination."""

    syntax_tree = ast.parse(source_code)
    all_optimizations = []

    for _ in range(5):

        previous_code = ast.unparse(syntax_tree)

        # Stage 1: Constant Propagation
        propagator = ConstantPropagator()

        syntax_tree = propagator.visit(syntax_tree)

        all_optimizations.extend(
            propagator.optimizations
        )

        # Stage 2: Constant Folding
        folder = ConstantFolder()

        syntax_tree = folder.visit(syntax_tree)

        all_optimizations.extend(
            folder.optimizations
        )

        # Stage 3: Dead Code Elimination
        eliminator = DeadCodeEliminator()

        syntax_tree = eliminator.eliminate(syntax_tree)

        all_optimizations.extend(
            eliminator.optimizations
        )

        current_code = ast.unparse(syntax_tree)

        if current_code == previous_code:
            break

    ast.fix_missing_locations(syntax_tree)

    return {
        "optimized_code": ast.unparse(syntax_tree),
        "optimizations": all_optimizations,
        "total_optimizations": len(all_optimizations)
    }
