
import ast


def generate_python_code(intermediate_code):
    """Generate Python source code from intermediate instructions."""

    generated_lines = []

    for instruction in intermediate_code:

        instruction = instruction.strip()

        if instruction.startswith("CALL "):
            instruction = instruction[5:]

        generated_lines.append(instruction)

    return "\n".join(generated_lines)


def generate_from_ast(syntax_tree):
    """Generate readable Python source code from an AST."""

    ast.fix_missing_locations(syntax_tree)

    return ast.unparse(syntax_tree)
