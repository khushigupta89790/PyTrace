from compiler.symbol_table import build_symbol_table


SOURCE_CODE = """
x = 10

def outer(a: int):
    y = 20

    def inner(b: float):
        z = a + b
        return z

    return y
"""


def test_symbol_table_creation():
    symbols = build_symbol_table(SOURCE_CODE)

    assert isinstance(symbols, list)
    assert len(symbols) > 0


def test_global_variable_scope():
    symbols = build_symbol_table(SOURCE_CODE)

    x = next(
        symbol for symbol in symbols
        if symbol["name"] == "x"
    )

    assert x["scope"] == "global"
    assert x["kind"] == "variable"
    assert x["data_type"] == "int"


def test_function_symbols():
    symbols = build_symbol_table(SOURCE_CODE)

    outer = next(
        symbol for symbol in symbols
        if symbol["name"] == "outer"
    )

    inner = next(
        symbol for symbol in symbols
        if symbol["name"] == "inner"
    )

    assert outer["kind"] == "function"
    assert inner["kind"] == "function"


def test_nested_function_scopes():
    symbols = build_symbol_table(SOURCE_CODE)

    a = next(
        symbol for symbol in symbols
        if symbol["name"] == "a"
    )

    b = next(
        symbol for symbol in symbols
        if symbol["name"] == "b"
    )

    assert a["scope"] == "outer@line4"
    assert b["scope"] == "inner@line7"


def test_parameter_types_and_variable_references():
    symbols = build_symbol_table(SOURCE_CODE)

    a = next(
        symbol for symbol in symbols
        if symbol["name"] == "a"
    )

    b = next(
        symbol for symbol in symbols
        if symbol["name"] == "b"
    )

    z = next(
        symbol for symbol in symbols
        if symbol["name"] == "z"
    )

    assert a["data_type"] == "int"
    assert b["data_type"] == "float"
    assert a["kind"] == "parameter"
    assert b["kind"] == "parameter"
    assert z["data_type"] == "float"
    assert z["references"] == 1