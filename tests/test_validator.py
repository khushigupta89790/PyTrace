
from pathlib import Path

from compiler.optimizer import optimize_code
from compiler.validator import (
    execute_code,
    validate_optimization
)


def test_execute_valid_python_code():
    source_code = """
print("Hello PyTrace")
"""

    result = execute_code(source_code)

    assert result["success"] is True
    assert result["output"] == "Hello PyTrace"
    assert result["error"] == ""
    assert result["return_code"] == 0


def test_execute_invalid_python_code():
    source_code = """
print(undefined_variable)
"""

    result = execute_code(source_code)

    assert result["success"] is False
    assert "NameError" in result["error"]
    assert result["return_code"] != 0


def test_validate_matching_outputs():
    original_code = """
x = 10
y = 20
print(x + y)
"""

    optimized_code = """
print(30)
"""

    result = validate_optimization(
        original_code,
        optimized_code
    )

    assert result["status"] == "PASSED"
    assert result["outputs_match"] is True
    assert result["original_output"] == "30"
    assert result["optimized_output"] == "30"


def test_validate_mismatched_outputs():
    original_code = """
print(100)
"""

    optimized_code = """
print(200)
"""

    result = validate_optimization(
        original_code,
        optimized_code
    )

    assert result["status"] == "FAILED"
    assert result["outputs_match"] is False


def test_validate_original_execution_failure():
    original_code = """
print(undefined_variable)
"""

    optimized_code = """
print(100)
"""

    result = validate_optimization(
        original_code,
        optimized_code
    )

    assert result["status"] == "ORIGINAL_EXECUTION_FAILED"
    assert result["outputs_match"] is False


def test_validate_sample_file():
    sample_path = (
        Path(__file__).parent.parent
        / "samples"
        / "sample.py"
    )

    assert sample_path.exists()

    original_code = sample_path.read_text(encoding="utf-8")

    optimization_result = optimize_code(original_code)

    validation = validate_optimization(
        original_code,
        optimization_result["optimized_code"]
    )

    assert validation["status"] == "PASSED"
    assert validation["outputs_match"] is True
