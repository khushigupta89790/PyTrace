
import subprocess
import sys
import tempfile
import os


def execute_code(source_code):
    """Execute Python code in a separate process and capture output."""

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            encoding="utf-8",
            delete=False
        ) as temp_file:

            temp_file.write(source_code)
            temp_path = temp_file.name

        result = subprocess.run(
            [sys.executable, temp_path],
            capture_output=True,
            text=True,
            timeout=5
        )

        return {
            "success": result.returncode == 0,
            "output": result.stdout.strip(),
            "error": result.stderr.strip(),
            "return_code": result.returncode
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "output": "",
            "error": "Execution timed out.",
            "return_code": None
        }

    except OSError as error:
        return {
            "success": False,
            "output": "",
            "error": str(error),
            "return_code": None
        }

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


def validate_optimization(original_code, optimized_code):
    """Compare the outputs of original and optimized programs."""

    original_result = execute_code(original_code)
    optimized_result = execute_code(optimized_code)

    if not original_result["success"]:
        status = "ORIGINAL_EXECUTION_FAILED"

    elif not optimized_result["success"]:
        status = "OPTIMIZED_EXECUTION_FAILED"

    elif original_result["output"] == optimized_result["output"]:
        status = "PASSED"

    else:
        status = "FAILED"

    return {
        "status": status,
        "original_output": original_result["output"],
        "optimized_output": optimized_result["output"],
        "original_error": original_result["error"],
        "optimized_error": optimized_result["error"],
        "outputs_match": (
            original_result["success"]
            and optimized_result["success"]
            and original_result["output"] == optimized_result["output"]
        )
    }
