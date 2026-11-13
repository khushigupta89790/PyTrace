
import ast
from collections import Counter


def parse_source(source_code):
    """
    Parse Python source code and generate an Abstract Syntax Tree.
    """

    if not isinstance(source_code, str):
        return {
            "success": False,
            "tree": None,
            "error": {
                "type": "InputError",
                "message": "Source code must be a string.",
                "line": None,
                "column": None
            }
        }

    if not source_code.strip():
        return {
            "success": False,
            "tree": None,
            "error": {
                "type": "InputError",
                "message": "Source code is empty.",
                "line": None,
                "column": None
            }
        }

    try:
        syntax_tree = ast.parse(source_code)

        return {
            "success": True,
            "tree": syntax_tree,
            "error": None
        }

    except SyntaxError as error:
        return {
            "success": False,
            "tree": None,
            "error": {
                "type": "SyntaxError",
                "message": error.msg,
                "line": error.lineno,
                "column": error.offset,
                "end_line": error.end_lineno,
                "end_column": error.end_offset,
                "source_line": error.text.strip() if error.text else None
            }
        }


def generate_ast_tree(syntax_tree):
    """
    Convert the AST into a readable tree representation.
    """

    return ast.dump(
        syntax_tree,
        indent=4,
        include_attributes=True
    )


def analyze_ast(syntax_tree):
    """
    Traverse the AST and collect detailed information about its nodes.
    """

    node_information = []

    for node in ast.walk(syntax_tree):

        node_information.append({
            "node_type": type(node).__name__,
            "line": getattr(node, "lineno", None),
            "column": getattr(node, "col_offset", None),
            "end_line": getattr(node, "end_lineno", None),
            "end_column": getattr(node, "end_col_offset", None)
        })

    return node_information


def summarize_ast(syntax_tree):
    """
    Generate a summary of AST node types and their frequencies.
    """

    node_types = Counter(
        type(node).__name__
        for node in ast.walk(syntax_tree)
    )

    return {
        "total_nodes": sum(node_types.values()),
        "node_types": dict(node_types)
    }


def build_ast_hierarchy(syntax_tree):
    """
    Build a parent-child hierarchy for AST visualization.
    """

    def build_node(node):

        return {
            "name": type(node).__name__,
            "children": [
                build_node(child)
                for child in ast.iter_child_nodes(node)
            ]
        }

    return build_node(syntax_tree)
