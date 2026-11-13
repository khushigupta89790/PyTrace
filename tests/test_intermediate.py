from compiler.intermediate import generate_intermediate_code


def test_arithmetic_intermediate_code():
    source_code = """
a = 10
b = 5
result = a + b
print(result)
"""

    instructions = generate_intermediate_code(source_code)

    assert isinstance(instructions, list)
    assert any("a + b" in instruction for instruction in instructions)
    assert any("result =" in instruction for instruction in instructions)
    assert any("CALL print" in instruction for instruction in instructions)


def test_comparison_intermediate_code():
    source_code = """
price = 500
result = price >= 100
"""

    instructions = generate_intermediate_code(source_code)

    assert any(">=" in instruction for instruction in instructions)


def test_if_else_intermediate_code():
    source_code = """
price = 500

if price > 100:
    result = 1
else:
    result = 0
"""

    instructions = generate_intermediate_code(source_code)

    assert any("IF_FALSE" in instruction for instruction in instructions)
    assert any("GOTO" in instruction for instruction in instructions)
    assert any("LABEL" in instruction for instruction in instructions)


def test_while_loop_intermediate_code():
    source_code = """
count = 0

while count < 3:
    count = count + 1
"""

    instructions = generate_intermediate_code(source_code)

    assert any("LABEL" in instruction for instruction in instructions)
    assert any("IF_FALSE" in instruction for instruction in instructions)
    assert any("GOTO" in instruction for instruction in instructions)


def test_function_intermediate_code():
    source_code = """
def calculate(a, b):
    result = a * b
    return result

answer = calculate(10, 5)
"""

    instructions = generate_intermediate_code(source_code)

    assert any("FUNCTION calculate" in instruction for instruction in instructions)
    assert any("RETURN" in instruction for instruction in instructions)
    assert any("END_FUNCTION calculate" in instruction for instruction in instructions)


def test_augmented_assignment_intermediate_code():
    source_code = """
count = 10
count += 5
"""

    instructions = generate_intermediate_code(source_code)

    assert any("+ 5" in instruction for instruction in instructions)


def test_unsupported_list_syntax():
    source_code = """
numbers = [10, 20, 30]
print(numbers)
"""

    try:
        generate_intermediate_code(source_code)
        assert False, "Expected NotImplementedError for list syntax"

    except NotImplementedError as error:
        assert "Unsupported expression: List" in str(error)