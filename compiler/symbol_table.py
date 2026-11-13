
import ast


class SymbolTableBuilder(ast.NodeVisitor):

    def __init__(self):
        self.symbols = {}
        self.scope_stack = ["global"]

    @property
    def current_scope(self):
        return self.scope_stack[-1]

    def get_scope_key(self, scope, name):
        return f"{scope}::{name}"

    def add_symbol(
        self,
        name,
        data_type="unknown",
        kind="variable",
        line=None
    ):
        """Add a new symbol or update an existing symbol."""

        key = self.get_scope_key(self.current_scope, name)

        if key not in self.symbols:
            self.symbols[key] = {
                "name": name,
                "kind": kind,
                "scope": self.current_scope,
                "data_type": data_type,
                "assignments": 0,
                "references": 0,
                "declaration_line": line
            }

        elif (
            data_type != "unknown"
            and self.symbols[key]["kind"] != "parameter"
        ):
            self.symbols[key]["data_type"] = data_type

        return self.symbols[key]

    def find_symbol(self, name):
        """Find a symbol in the current or enclosing scopes."""

        for scope in reversed(self.scope_stack):
            key = self.get_scope_key(scope, name)

            if key in self.symbols:
                return self.symbols[key]

        return None

    def get_data_type(self, node):
        """Infer the data type of a Python expression."""

        if isinstance(node, ast.Constant):
            return type(node.value).__name__

        elif isinstance(node, ast.Name):
            symbol = self.find_symbol(node.id)

            if symbol:
                return symbol["data_type"]

            return "unknown"

        elif isinstance(node, ast.BinOp):
            left_type = self.get_data_type(node.left)
            right_type = self.get_data_type(node.right)

            if isinstance(node.op, ast.Div):
                return "float"

            if left_type == right_type:
                return left_type

            if (
                left_type in ("int", "float")
                and right_type in ("int", "float")
            ):
                return "float"

            if (
                isinstance(node.op, ast.Add)
                and left_type == right_type == "str"
            ):
                return "str"

            return "unknown"

        elif isinstance(node, ast.Compare):
            return "bool"

        elif isinstance(node, (ast.BoolOp, ast.UnaryOp)):
            if isinstance(node, ast.UnaryOp) and isinstance(
                node.op, (ast.USub, ast.UAdd, ast.Invert)
            ):
                return self.get_data_type(node.operand)

            return "bool"

        elif isinstance(node, (ast.List, ast.ListComp)):
            return "list"

        elif isinstance(node, ast.Tuple):
            return "tuple"

        elif isinstance(node, ast.GeneratorExp):
            return "generator"

        elif isinstance(node, ast.Dict):
            return "dict"

        elif isinstance(node, (ast.Set, ast.SetComp)):
            return "set"

        elif isinstance(node, ast.Constant):
            return type(node.value).__name__

        elif isinstance(node, ast.IfExp):
            body_type = self.get_data_type(node.body)
            else_type = self.get_data_type(node.orelse)

            if body_type == else_type:
                return body_type

            if (
                body_type in ("int", "float")
                and else_type in ("int", "float")
            ):
                return "float"

            return "unknown"

        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):

                built_in_types = {
                    "int": "int",
                    "float": "float",
                    "str": "str",
                    "bool": "bool",
                    "list": "list",
                    "tuple": "tuple",
                    "dict": "dict",
                    "set": "set",
                    "len": "int"
                }

                return built_in_types.get(
                    node.func.id,
                    "unknown"
                )

        return "unknown"

    def visit_Assign(self, node):
        """Process normal assignments."""

        data_type = self.get_data_type(node.value)

        self.visit(node.value)

        for target in node.targets:

            if isinstance(target, ast.Name):
                symbol = self.add_symbol(
                    target.id,
                    data_type,
                    line=node.lineno
                )

                symbol["assignments"] += 1

            else:
                self.visit(target)

    def visit_AnnAssign(self, node):
        """Process annotated assignments."""

        data_type = (
            self.get_data_type(node.value)
            if node.value else "unknown"
        )

        if node.annotation:
            annotation = ast.unparse(node.annotation)

            if annotation in (
                "int", "float", "str", "bool",
                "list", "tuple", "dict", "set"
            ):
                data_type = annotation

        if node.value:
            self.visit(node.value)

        if isinstance(node.target, ast.Name):
            symbol = self.add_symbol(
                node.target.id,
                data_type,
                line=node.lineno
            )

            symbol["assignments"] += 1

        else:
            self.visit(node.target)

    def visit_AugAssign(self, node):
        """Process augmented assignments such as x += 1."""

        self.visit(node.value)

        if isinstance(node.target, ast.Name):
            symbol = self.add_symbol(
                node.target.id,
                line=node.lineno
            )

            symbol["assignments"] += 1
            symbol["references"] += 1

            new_type = self.get_data_type(node.value)

            if new_type != "unknown":
                symbol["data_type"] = new_type

        else:
            self.visit(node.target)

    def visit_Name(self, node):
        """Track references to previously declared symbols."""

        if isinstance(node.ctx, ast.Load):
            symbol = self.find_symbol(node.id)

            if symbol:
                symbol["references"] += 1

    def visit_FunctionDef(self, node):
        """Register functions and create separate function scopes."""

        function_symbol = self.add_symbol(
            node.name,
            data_type="function",
            kind="function",
            line=node.lineno
        )

        function_symbol["assignments"] += 1

        # Evaluate decorators and default values in the enclosing scope.
        for decorator in node.decorator_list:
            self.visit(decorator)

        for default in node.args.defaults:
            self.visit(default)

        for default in node.args.kw_defaults:
            if default:
                self.visit(default)

        function_scope = f"{node.name}@line{node.lineno}"
        self.scope_stack.append(function_scope)

        # Register function parameters.
        arguments = (
            node.args.posonlyargs
            + node.args.args
            + node.args.kwonlyargs
        )

        if node.args.vararg:
            arguments.append(node.args.vararg)

        if node.args.kwarg:
            arguments.append(node.args.kwarg)

        for argument in arguments:
            parameter_type = "unknown"

            if argument.annotation:
                annotation = ast.unparse(argument.annotation)

                if annotation in (
                    "int", "float", "str", "bool",
                    "list", "tuple", "dict", "set"
                ):
                    parameter_type = annotation

            parameter = self.add_symbol(
                argument.arg,
                parameter_type,
                kind="parameter",
                line=argument.lineno
            )

            parameter["assignments"] += 1

        for statement in node.body:
            self.visit(statement)

        self.scope_stack.pop()

    def visit_AsyncFunctionDef(self, node):
        """Handle asynchronous function definitions."""

        self.visit_FunctionDef(node)

    def get_symbol_table(self):
        """Return all symbols as a list of dictionaries."""

        return list(self.symbols.values())


def build_symbol_table(source_code):
    """Build a scope-aware symbol table from Python source."""

    syntax_tree = ast.parse(source_code)

    builder = SymbolTableBuilder()
    builder.visit(syntax_tree)

    return builder.get_symbol_table()
