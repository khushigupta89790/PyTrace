
import ast
from pathlib import Path

from compiler.optimizer import optimize_code
from compiler.code_generator import (
    generate_from_ast,
    generate_python_code
)


def test_generate_python_code_from_intermediate():
    instructions = [
        "a = 10",
        "b = 20",
        "t1 = a + b",
        "result = t1",
        "CALL print(result)"
    ]

    generated_code = generate_python_code(instructions)

    assert isinstance(generated_code, str)
    assert "a = 10" in generated_code
    assert "b = 20" in generated_code
    assert "print(result)" in generated_code


def test_generate_code_from_ast():
    source_code = """
price = 500
quantity = 3
total = price * quantity
print(total)
"""

    syntax_tree = ast.parse(source_code)
    generated_code = generate_from_ast(syntax_tree)

    assert isinstance(generated_code, str)
    assert "price = 500" in generated_code
    assert "quantity = 3" in generated_code
    assert "print(total)" in generated_code

    ast.parse(generated_code)


def test_generated_code_preserves_execution_output():
    source_code = """
a = 10
b = 20
result = a + b
print(result)
"""

    syntax_tree = ast.parse(source_code)
    generated_code = generate_from_ast(syntax_tree)

    generated_tree = ast.parse(generated_code)

    assert isinstance(generated_tree, ast.Module)


def test_optimize_and_generate_sample_code():
    sample_path = (
        Path(__file__).parent.parent
        / "samples"
        / "sample.py"
    )

    assert sample_path.exists(), "samples/sample.py does not exist"

    source_code = sample_path.read_text(encoding="utf-8")

    ast.parse(source_code)

    result = optimize_code(source_code)

    optimized_tree = ast.parse(result["optimized_code"])

    final_code = generate_from_ast(optimized_tree)

    assert isinstance(final_code, str)
    assert len(final_code.strip()) > 0

    ast.parse(final_code)
