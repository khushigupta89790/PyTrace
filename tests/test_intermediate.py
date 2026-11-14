
from compiler.intermediate import generate_intermediate_code

def test_list_intermediate_code():
    source_code = """
numbers = [10, 20, 30]
print(numbers)
"""

    instructions = generate_intermediate_code(source_code)

    assert any("LIST" in instruction for instruction in instructions)
    assert any("CALL print" in instruction for instruction in instructions)


def test_tuple_intermediate_code():
    source_code = """
values = (10, 20, 30)
"""

    instructions = generate_intermediate_code(source_code)

    assert any("TUPLE" in instruction for instruction in instructions)


def test_dictionary_intermediate_code():
    source_code = """
student = {"name": "Riya", "marks": 95}
"""

    instructions = generate_intermediate_code(source_code)

    assert any("DICT" in instruction for instruction in instructions)


def test_list_indexing_intermediate_code():
    source_code = """
numbers = [10, 20, 30]
first = numbers[0]
"""

    instructions = generate_intermediate_code(source_code)

    assert any("LIST" in instruction for instruction in instructions)
    assert any("[0]" in instruction for instruction in instructions)
