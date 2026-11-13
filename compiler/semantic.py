
import ast
import builtins


class SemanticAnalyzer(ast.NodeVisitor):

    def __init__(self):
        self.scope_stack = ["global"]
        self.defined_variables = {"global": set()}

        self.used_variables = set()
        self.errors = []
        self.warnings = []
        self.assignments = {}
        self.declarations = {}
        self.imported_names = set()

    @property
    def current_scope(self):
        return self.scope_stack[-1]

    def scope_key(self, scope, name):
        return f"{scope}::{name}"

    def add_variable(self, name, line=None, kind="variable"):
        """Register a variable in the current scope."""

        scope = self.current_scope
        self.defined_variables.setdefault(scope, set())
        self.defined_variables[scope].add(name)

        key = self.scope_key(scope, name)
        self.assignments[key] = self.assignments.get(key, 0) + 1

        if key not in self.declarations:
            self.declarations[key] = {
                "name": name,
                "scope": scope,
                "kind": kind,
                "line": line
            }

    def find_variable_scope(self, name):
        """Find the scope where a variable is defined."""

        for scope in reversed(self.scope_stack):
            if name in self.defined_variables.get(scope, set()):
                return scope

        return None

    def is_defined(self, name):
        """Check whether a variable or built-in name exists."""

        return (
            self.find_variable_scope(name) is not None
            or hasattr(builtins, name)
            or name in self.imported_names
        )

    def visit_Name(self, node):
        """Check variable references and definitions."""

        if isinstance(node.ctx, ast.Load):

            defining_scope = self.find_variable_scope(node.id)

            if defining_scope is not None:
                self.used_variables.add(
                    self.scope_key(defining_scope, node.id)
                )

            elif not (
                hasattr(builtins, node.id)
                or node.id in self.imported_names
            ):
                self.errors.append({
                    "type": "Undefined Variable",
                    "message": (
                        f"Variable '{node.id}' is used before "
                        "assignment or declaration."
                    ),
                    "line": node.lineno,
                    "column": node.col_offset,
                    "scope": self.current_scope
                })

        elif isinstance(node.ctx, ast.Store):
            self.add_variable(
                node.id,
                getattr(node, "lineno", None)
            )

    def visit_Assign(self, node):
        """Process normal assignments."""

        self.visit(node.value)

        for target in node.targets:
            self.visit(target)

    def visit_AnnAssign(self, node):
        """Process annotated assignments."""

        if node.value:
            self.visit(node.value)

        self.visit(node.target)

    def visit_AugAssign(self, node):
        """Process augmented assignments."""

        self.visit(node.target)
        self.visit(node.value)
        self.visit(node.target)

    def visit_Import(self, node):
        """Register imported modules."""

        for alias in node.names:
            name = alias.asname or alias.name.split(".")[0]

            self.add_variable(name, node.lineno, kind="import")
            self.imported_names.add(name)

    def visit_ImportFrom(self, node):
        """Register imported names."""

        for alias in node.names:

            if alias.name == "*":
                continue

            name = alias.asname or alias.name

            self.add_variable(name, node.lineno, kind="import")
            self.imported_names.add(name)

    def visit_FunctionDef(self, node):
        """Register functions and analyze their local scopes."""

        self.add_variable(
            node.name,
            node.lineno,
            kind="function"
        )

        for decorator in node.decorator_list:
            self.visit(decorator)

        for default in node.args.defaults:
            self.visit(default)

        for default in node.args.kw_defaults:
            if default:
                self.visit(default)

        function_scope = f"{node.name}@line{node.lineno}"

        self.scope_stack.append(function_scope)
        self.defined_variables[function_scope] = set()

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
            self.add_variable(
                argument.arg,
                argument.lineno,
                kind="parameter"
            )

            if argument.annotation:
                self.visit(argument.annotation)

        if node.returns:
            self.visit(node.returns)

        for statement in node.body:
            self.visit(statement)

        self.scope_stack.pop()

    def visit_AsyncFunctionDef(self, node):
        """Handle asynchronous function definitions."""

        self.visit_FunctionDef(node)

    def visit_ClassDef(self, node):
        """Register a class and analyze its body."""

        self.add_variable(
            node.name,
            node.lineno,
            kind="class"
        )

        for decorator in node.decorator_list:
            self.visit(decorator)

        for base in node.bases:
            self.visit(base)

        for keyword_node in node.keywords:
            self.visit(keyword_node.value)

        class_scope = f"{node.name}@line{node.lineno}"

        self.scope_stack.append(class_scope)
        self.defined_variables[class_scope] = set()

        for statement in node.body:
            self.visit(statement)

        self.scope_stack.pop()

    def analyze(self, syntax_tree):
        """Run semantic analysis and generate diagnostics."""

        self.visit(syntax_tree)

        for key, count in self.assignments.items():

            declaration = self.declarations[key]
            name = declaration["name"]
            kind = declaration["kind"]

            if (
                key not in self.used_variables
                and kind == "variable"
            ):
                self.warnings.append({
                    "type": "Unused Variable",
                    "message": (
                        f"Variable '{name}' is assigned "
                        "but never used."
                    ),
                    "line": declaration["line"],
                    "scope": declaration["scope"]
                })

            if count > 1:
                self.warnings.append({
                    "type": "Multiple Assignments",
                    "message": f"'{name}' is assigned {count} times.",
                    "line": declaration["line"],
                    "scope": declaration["scope"]
                })

        return {
            "errors": self.errors,
            "warnings": self.warnings,
            "total_errors": len(self.errors),
            "total_warnings": len(self.warnings)
        }


def analyze_semantics(source_code):
    """Perform semantic analysis on Python source code."""

    try:
        syntax_tree = ast.parse(source_code)

    except SyntaxError as error:
        return {
            "errors": [{
                "type": "Syntax Error",
                "message": error.msg,
                "line": error.lineno,
                "column": error.offset,
                "scope": "global"
            }],
            "warnings": [],
            "total_errors": 1,
            "total_warnings": 0
        }

    analyzer = SemanticAnalyzer()
    return analyzer.analyze(syntax_tree)
