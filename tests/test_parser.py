from compiler.parser import (
    parse_source,
    generate_ast_tree,
    analyze_ast,
    summarize_ast,
    build_ast_hierarchy
)


SOURCE_CODE = """
price = 500
quantity = 3
total = price * quantity

if total >= 1000:
    print("High value")
else:
    print("Low value")
"""


def test_parse_valid_python_code():
    result = parse_source(SOURCE_CODE)

    assert result["success"] is True
    assert result["tree"] is not None
    assert result["error"] is None


def test_parse_invalid_python_code():
    source_code = """
price = 500
if price > 100:
    print(price
"""

    result = parse_source(source_code)

    assert result["success"] is False
    assert result["tree"] is None
    assert result["error"]["type"] == "SyntaxError"
    assert result["error"]["line"] is not None


def test_parse_empty_source_code():
    result = parse_source("")

    assert result["success"] is False
    assert result["tree"] is None
    assert result["error"]["type"] == "InputError"


def test_generate_ast_tree():
    result = parse_source(SOURCE_CODE)

    syntax_tree = result["tree"]
    ast_representation = generate_ast_tree(syntax_tree)

    assert isinstance(ast_representation, str)
    assert "Module" in ast_representation
    assert "Assign" in ast_representation


def test_analyze_ast_nodes():
    result = parse_source(SOURCE_CODE)

    nodes = analyze_ast(result["tree"])

    assert len(nodes) > 0
    assert any(node["node_type"] == "Module" for node in nodes)
    assert any(node["node_type"] == "Assign" for node in nodes)
    assert any(node["node_type"] == "If" for node in nodes)


def test_summarize_ast():
    result = parse_source(SOURCE_CODE)

    summary = summarize_ast(result["tree"])

    assert summary["total_nodes"] > 0
    assert "Module" in summary["node_types"]
    assert "Assign" in summary["node_types"]
    assert "If" in summary["node_types"]


def test_build_ast_hierarchy():
    result = parse_source(SOURCE_CODE)

    hierarchy = build_ast_hierarchy(result["tree"])

    assert hierarchy["name"] == "Module"
    assert isinstance(hierarchy["children"], list)
    assert len(hierarchy["children"]) > 0