from compiler.optimizer import optimize_code
from compiler.validator import validate_optimization


def test_optimizer_validation():
    source_code = """
price = 500
quantity = 4
discount = 100

subtotal = price * quantity
final_price = subtotal - discount

print("Final Price:", final_price)
"""

    result = optimize_code(source_code)

    assert isinstance(result["optimized_code"], str)
    assert len(result["optimizations"]) > 0

    validation = validate_optimization(
        source_code,
        result["optimized_code"]
    )

    assert validation["status"] == "PASSED"
    assert validation["outputs_match"] is True
    assert validation["original_output"] == "Final Price: 1900"
    assert validation["optimized_output"] == "Final Price: 1900"


def test_constant_folding():
    source_code = """
a = 10 + 5
b = 4 * 6
print(a, b)
"""

    result = optimize_code(source_code)

    assert "15" in result["optimized_code"]
    assert "24" in result["optimized_code"]
    assert len(result["optimizations"]) > 0


def test_constant_propagation():
    source_code = """
x = 10
y = x + 5
x = 20
z = x + 10
print(y, z)
"""

    result = optimize_code(source_code)

    validation = validate_optimization(
        source_code,
        result["optimized_code"]
    )

    assert validation["status"] == "PASSED"
    assert validation["original_output"] == "15 30"
    assert validation["optimized_output"] == "15 30"


def test_function_scope_safety():
    source_code = """
x = 10

def calculate():
    x = 20
    result = x + 5
    print(result)

calculate()
print(x)
"""

    result = optimize_code(source_code)

    validation = validate_optimization(
        source_code,
        result["optimized_code"]
    )

    assert validation["status"] == "PASSED"
    assert validation["original_output"] == "25\n10"
    assert validation["optimized_output"] == "25\n10"


def test_division_by_zero_is_not_folded():
    source_code = """
d = 10 / 0
print(d)
"""

    result = optimize_code(source_code)

    assert "10 / 0" in result["optimized_code"]

    validation = validate_optimization(
        source_code,
        result["optimized_code"]
    )

    assert validation["status"] == "ORIGINAL_EXECUTION_FAILED"