
from pathlib import Path

from compiler.pipeline import run_pipeline


SAMPLE_PATH = (
    Path(__file__).parent.parent
    / "samples"
    / "sample.py"
)


def test_pipeline_sample_file():
    assert SAMPLE_PATH.exists()

    source_code = SAMPLE_PATH.read_text(encoding="utf-8")

    results = run_pipeline(source_code, validate=True)

    assert results["status"] == "COMPLETED"
    assert len(results["tokens"]) > 0
    assert len(results["ast"]) > 0
    assert len(results["symbol_table"]) > 0
    assert results["semantic"]["total_errors"] == 0
    assert len(results["intermediate_code"]) > 0
    assert results["optimized_code"] is not None
    assert results["generated_code"] is not None
    assert results["validation"]["status"] == "PASSED"


def test_pipeline_lexical_error():
    source_code = '''
print("Hello
'''

    results = run_pipeline(source_code)

    assert results["status"] == "LEXICAL_ERROR"
    assert results["error"] is not None


def test_pipeline_syntax_error():
    source_code = """
price = 100
if price > 50
    print(price)
"""

    results = run_pipeline(source_code)

    assert results["status"] == "SYNTAX_ERROR"
    assert results["error"]["type"] == "SyntaxError"


def test_pipeline_semantic_error():
    source_code = """
price = 100
total = price + discount
print(total)
"""

    results = run_pipeline(source_code)

    assert results["status"] == "SEMANTIC_ISSUES"
    assert results["semantic"]["total_errors"] > 0
    assert results["optimized_code"] is None


def test_pipeline_without_validation():
    source_code = """
a = 10
b = 20
result = a + b
print(result)
"""

    results = run_pipeline(source_code, validate=False)

    assert results["status"] == "COMPLETED"
    assert results["generated_code"] is not None
    assert results["validation"] is None


def test_pipeline_returns_optimization_details():
    source_code = """
price = 500
quantity = 3
total = price * quantity
print(total)
"""

    results = run_pipeline(source_code)

    assert results["status"] == "COMPLETED"
    assert isinstance(results["optimizations"], list)
    assert isinstance(results["optimized_code"], str)
    assert isinstance(results["generated_code"], str)
