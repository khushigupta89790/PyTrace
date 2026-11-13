from compiler.semantic import analyze_semantics


def test_import_and_reassignment():
    source_code = """
import math

price = 100
price = 200

result = math.sqrt(price)

print(result)
"""

    result = analyze_semantics(source_code)

    assert result["total_errors"] == 0
    assert result["total_warnings"] == 1

    warning = result["warnings"][0]

    assert warning["type"] == "Multiple Assignments"
    assert "'price' is assigned 2 times." in warning["message"]


def test_undefined_variable_detection():
    source_code = """
price = 100
total = price + discount
print(total)
"""

    result = analyze_semantics(source_code)

    assert result["total_errors"] == 1
    assert result["errors"][0]["type"] == "Undefined Variable"
    assert "discount" in result["errors"][0]["message"]


def test_unused_variable_detection():
    source_code = """
price = 100
quantity = 5
print(price)
"""

    result = analyze_semantics(source_code)

    assert result["total_errors"] == 0
    assert result["total_warnings"] == 1
    assert result["warnings"][0]["type"] == "Unused Variable"
    assert "quantity" in result["warnings"][0]["message"]


def test_nested_function_variable_usage():
    source_code = """
def outer():
    value = 100

    def inner():
        return value

    return inner()
"""

    result = analyze_semantics(source_code)

    assert result["total_errors"] == 0
    assert result["total_warnings"] == 0


def test_syntax_error_detection():
    source_code = """
price = 100
if price > 50:
    print(price
"""

    result = analyze_semantics(source_code)

    assert result["total_errors"] == 1
    assert result["errors"][0]["type"] == "Syntax Error"
    assert result["errors"][0]["line"] is not None