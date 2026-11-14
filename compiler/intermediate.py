
import ast


class IntermediateCodeGenerator(ast.NodeVisitor):

    def __init__(self):
        self.instructions = []
        self.temp_count = 0
        self.label_count = 0

    def new_temp(self):
        """Generate a temporary variable."""
        self.temp_count += 1
        return f"t{self.temp_count}"

    def new_label(self):
        """Generate a unique label."""
        self.label_count += 1
        return f"L{self.label_count}"

    def emit(self, instruction):
        """Append an instruction to the IR."""
        self.instructions.append(instruction)

    def generate_slice_index(self, node):
        """Generate an index or slice expression."""

        if isinstance(node, ast.Slice):
            lower = (
                self.generate_expression(node.lower)
                if node.lower is not None else ""
            )
            upper = (
                self.generate_expression(node.upper)
                if node.upper is not None else ""
            )
            step = (
                self.generate_expression(node.step)
                if node.step is not None else ""
            )

            result = f"{lower}:{upper}"

            if node.step is not None:
                result += f":{step}"

            return result

        return self.generate_expression(node)

    def generate_expression(self, node):
        """Convert expressions into three-address instructions."""

        if isinstance(node, ast.Constant):
            return repr(node.value)

        elif isinstance(node, ast.Name):
            return node.id

        elif isinstance(node, ast.BinOp):

            left = self.generate_expression(node.left)
            right = self.generate_expression(node.right)

            operators = {
                ast.Add: "+",
                ast.Sub: "-",
                ast.Mult: "*",
                ast.Div: "/",
                ast.FloorDiv: "//",
                ast.Mod: "%",
                ast.Pow: "**"
            }

            operator = operators.get(type(node.op))

            if operator is None:
                raise NotImplementedError(
                    f"Unsupported binary operator: {type(node.op).__name__}"
                )

            temp = self.new_temp()
            self.emit(f"{temp} = {left} {operator} {right}")

            return temp

        elif isinstance(node, ast.UnaryOp):

            operand = self.generate_expression(node.operand)

            operators = {
                ast.USub: "-",
                ast.UAdd: "+",
                ast.Not: "not ",
                ast.Invert: "~"
            }

            operator = operators.get(type(node.op))

            if operator is None:
                raise NotImplementedError(
                    f"Unsupported unary operator: {type(node.op).__name__}"
                )

            temp = self.new_temp()
            self.emit(f"{temp} = {operator}{operand}")

            return temp

        elif isinstance(node, ast.Compare):

            left = self.generate_expression(node.left)

            operators = {
                ast.Eq: "==",
                ast.NotEq: "!=",
                ast.Lt: "<",
                ast.LtE: "<=",
                ast.Gt: ">",
                ast.GtE: ">=",
                ast.Is: "is",
                ast.IsNot: "is not",
                ast.In: "in",
                ast.NotIn: "not in"
            }

            results = []

            for operation, comparator in zip(
                node.ops, node.comparators
            ):

                right = self.generate_expression(comparator)

                operator = operators.get(type(operation))

                if operator is None:
                    raise NotImplementedError(
                        f"Unsupported comparison: {type(operation).__name__}"
                    )

                temp = self.new_temp()

                self.emit(
                    f"{temp} = {left} {operator} {right}"
                )

                results.append(temp)
                left = right

            if len(results) == 1:
                return results[0]

            combined = results[0]

            for result in results[1:]:
                temp = self.new_temp()
                self.emit(f"{temp} = {combined} and {result}")
                combined = temp

            return combined

        elif isinstance(node, ast.BoolOp):

            values = [
                self.generate_expression(value)
                for value in node.values
            ]

            operator = (
                "and" if isinstance(node.op, ast.And) else "or"
            )

            result = values[0]

            for value in values[1:]:
                temp = self.new_temp()
                self.emit(f"{temp} = {result} {operator} {value}")
                result = temp

            return result

        elif isinstance(node, ast.Call):

            function_name = self.expression_name(node.func)

            arguments = [
                self.generate_expression(arg)
                for arg in node.args
            ]

            for keyword_node in node.keywords:
                value = self.generate_expression(keyword_node.value)

                if keyword_node.arg is None:
                    arguments.append(f"**{value}")
                else:
                    arguments.append(
                        f"{keyword_node.arg}={value}"
                    )

            temp = self.new_temp()

            self.emit(
                f"{temp} = CALL {function_name}"
                f"({', '.join(arguments)})"
            )

            return temp

        elif isinstance(node, ast.IfExp):

            condition = self.generate_expression(node.test)

            else_label = self.new_label()
            end_label = self.new_label()
            result = self.new_temp()

            self.emit(f"IF_FALSE {condition} GOTO {else_label}")

            body_value = self.generate_expression(node.body)
            self.emit(f"{result} = {body_value}")
            self.emit(f"GOTO {end_label}")

            self.emit(f"LABEL {else_label}")

            else_value = self.generate_expression(node.orelse)
            self.emit(f"{result} = {else_value}")

            self.emit(f"LABEL {end_label}")

            return result

        # LIST SUPPORT
        elif isinstance(node, ast.List):

            elements = [
                self.generate_expression(element)
                for element in node.elts
            ]

            temp = self.new_temp()

            self.emit(
                f"{temp} = LIST [{', '.join(elements)}]"
            )

            return temp

        # TUPLE SUPPORT
        elif isinstance(node, ast.Tuple):

            elements = [
                self.generate_expression(element)
                for element in node.elts
            ]

            temp = self.new_temp()

            self.emit(
                f"{temp} = TUPLE ({', '.join(elements)})"
            )

            return temp

        # SET SUPPORT
        elif isinstance(node, ast.Set):

            elements = [
                self.generate_expression(element)
                for element in node.elts
            ]

            temp = self.new_temp()

            self.emit(
                f"{temp} = SET {{{', '.join(elements)}}}"
            )

            return temp

        # DICTIONARY SUPPORT
        elif isinstance(node, ast.Dict):

            entries = []

            for key, value in zip(node.keys, node.values):

                if key is None:
                    raise NotImplementedError(
                        "Dictionary unpacking is not supported."
                    )

                key_value = self.generate_expression(key)
                item_value = self.generate_expression(value)

                entries.append(
                    f"{key_value}: {item_value}"
                )

            temp = self.new_temp()

            self.emit(
                f"{temp} = DICT {{{', '.join(entries)}}}"
            )

            return temp

        # INDEXING AND SLICING SUPPORT
        elif isinstance(node, ast.Subscript):

            container = self.generate_expression(node.value)
            index = self.generate_slice_index(node.slice)

            temp = self.new_temp()

            self.emit(
                f"{temp} = {container}[{index}]"
            )

            return temp

        # ATTRIBUTE ACCESS SUPPORT
        elif isinstance(node, ast.Attribute):

            value = self.generate_expression(node.value)

            return f"{value}.{node.attr}"

        else:
            raise NotImplementedError(
                f"Unsupported expression: {type(node).__name__}"
            )

    def expression_name(self, node):
        """Get a readable name for a callable expression."""

        if isinstance(node, ast.Name):
            return node.id

        return ast.unparse(node)

    def visit_Assign(self, node):
        """Generate code for assignments."""

        value = self.generate_expression(node.value)

        for target in node.targets:

            if isinstance(target, ast.Name):

                self.emit(f"{target.id} = {value}")

            elif isinstance(target, ast.Subscript):

                container = self.generate_expression(target.value)
                index = self.generate_slice_index(target.slice)

                self.emit(
                    f"{container}[{index}] = {value}"
                )

            elif isinstance(target, ast.Attribute):

                obj = self.generate_expression(target.value)

                self.emit(
                    f"{obj}.{target.attr} = {value}"
                )

            else:
                raise NotImplementedError(
                    "Unsupported assignment target."
                )

    def visit_AnnAssign(self, node):
        """Generate code for annotated assignments."""

        if node.value is not None:

            value = self.generate_expression(node.value)

            if isinstance(node.target, ast.Name):

                self.emit(f"{node.target.id} = {value}")

            else:
                raise NotImplementedError(
                    "Only simple annotated variable assignments are supported."
                )

    def visit_AugAssign(self, node):
        """Generate code for augmented assignments."""

        operators = {
            ast.Add: "+",
            ast.Sub: "-",
            ast.Mult: "*",
            ast.Div: "/",
            ast.FloorDiv: "//",
            ast.Mod: "%",
            ast.Pow: "**"
        }

        operator = operators.get(type(node.op))

        if operator is None:
            raise NotImplementedError(
                f"Unsupported augmented operator: {type(node.op).__name__}"
            )

        right = self.generate_expression(node.value)

        if isinstance(node.target, ast.Name):

            target = node.target.id

        elif isinstance(node.target, ast.Subscript):

            container = self.generate_expression(node.target.value)
            index = self.generate_slice_index(node.target.slice)
            target = f"{container}[{index}]"

        else:
            raise NotImplementedError(
                "Unsupported augmented assignment target."
            )

        self.emit(
            f"{target} = {target} {operator} {right}"
        )

    def visit_Expr(self, node):
        """Handle standalone expressions and function calls."""

        if isinstance(node.value, ast.Call):

            function_name = self.expression_name(node.value.func)

            arguments = [
                self.generate_expression(arg)
                for arg in node.value.args
            ]

            for keyword_node in node.value.keywords:

                value = self.generate_expression(keyword_node.value)

                if keyword_node.arg is None:
                    arguments.append(f"**{value}")
                else:
                    arguments.append(
                        f"{keyword_node.arg}={value}"
                    )

            self.emit(
                f"CALL {function_name}({', '.join(arguments)})"
            )

        else:
            self.generate_expression(node.value)

    def visit_If(self, node):
        """Generate conditional branch instructions."""

        condition = self.generate_expression(node.test)

        else_label = self.new_label()
        end_label = self.new_label()

        self.emit(f"IF_FALSE {condition} GOTO {else_label}")

        for statement in node.body:
            self.visit(statement)

        if node.orelse:
            self.emit(f"GOTO {end_label}")

        self.emit(f"LABEL {else_label}")

        for statement in node.orelse:
            self.visit(statement)

        if node.orelse:
            self.emit(f"LABEL {end_label}")

    def visit_While(self, node):
        """Generate intermediate code for while loops."""

        start_label = self.new_label()
        end_label = self.new_label()

        self.emit(f"LABEL {start_label}")

        condition = self.generate_expression(node.test)

        self.emit(f"IF_FALSE {condition} GOTO {end_label}")

        for statement in node.body:
            self.visit(statement)

        self.emit(f"GOTO {start_label}")
        self.emit(f"LABEL {end_label}")

        for statement in node.orelse:
            self.visit(statement)

    def visit_For(self, node):
        """Generate abstract iterator instructions for for loops."""

        if not isinstance(node.target, ast.Name):
            raise NotImplementedError(
                "Only simple variable loop targets are supported."
            )

        iterable = self.generate_expression(node.iter)

        iterator = self.new_temp()
        start_label = self.new_label()
        end_label = self.new_label()

        self.emit(f"{iterator} = ITER_INIT {iterable}")
        self.emit(f"LABEL {start_label}")

        self.emit(
            f"{node.target.id} = ITER_NEXT {iterator}"
        )

        self.emit(
            f"IF_ITER_DONE {node.target.id} GOTO {end_label}"
        )

        for statement in node.body:
            self.visit(statement)

        self.emit(f"GOTO {start_label}")
        self.emit(f"LABEL {end_label}")

        for statement in node.orelse:
            self.visit(statement)

    def visit_FunctionDef(self, node):
        """Generate intermediate code for function definitions."""

        arguments = [
            arg.arg
            for arg in (
                node.args.posonlyargs
                + node.args.args
                + node.args.kwonlyargs
            )
        ]

        if node.args.vararg:
            arguments.append("*" + node.args.vararg.arg)

        if node.args.kwarg:
            arguments.append("**" + node.args.kwarg.arg)

        self.emit(
            f"FUNCTION {node.name}({', '.join(arguments)})"
        )

        for statement in node.body:
            self.visit(statement)

        self.emit(f"END_FUNCTION {node.name}")

    def visit_AsyncFunctionDef(self, node):
        """Handle asynchronous function definitions."""

        self.visit_FunctionDef(node)

    def visit_Return(self, node):
        """Generate return instructions."""

        if node.value is None:
            self.emit("RETURN")

        else:
            value = self.generate_expression(node.value)
            self.emit(f"RETURN {value}")

    def visit_Pass(self, node):
        self.emit("PASS")

    def visit_Break(self, node):
        self.emit("BREAK")

    def visit_Continue(self, node):
        self.emit("CONTINUE")

    def generate(self, syntax_tree):
        """Generate intermediate code from an AST."""

        self.instructions = []
        self.temp_count = 0
        self.label_count = 0

        for statement in syntax_tree.body:
            self.visit(statement)

        return self.instructions


def generate_intermediate_code(source_code):
    """Generate intermediate code from Python source."""

    syntax_tree = ast.parse(source_code)

    generator = IntermediateCodeGenerator()

    return generator.generate(syntax_tree)
