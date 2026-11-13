from compiler.lexer import analyze_tokens


def test_lexer_valid_python_code():

    source_code = """
price = 500
quantity = 3
total = price * quantity

if total >= 1000:
    print("High value")
else:
    print("Low value")
"""

    tokens, error = analyze_tokens(source_code)

    assert error is None
    assert len(tokens) > 0

    token_types = [item["token_type"] for item in tokens]

    assert "IDENTIFIER" in token_types
    assert "NUMBER" in token_types
    assert "KEYWORD" in token_types
    assert "STRING" in token_types
    assert "COMPARISON_OPERATOR" in token_types
    assert "BUILTIN_FUNCTION" in token_types


def test_lexer_token_positions():

    source_code = "price = 500"

    tokens, error = analyze_tokens(source_code)

    assert error is None
    assert len(tokens) == 3

    assert tokens[0]["lexeme"] == "price"
    assert tokens[0]["line"] == 1
    assert tokens[0]["column"] == 0

    assert tokens[1]["lexeme"] == "="
    assert tokens[2]["lexeme"] == "500"


def test_lexer_invalid_python_code():

    source_code = """
price = 500
if price > 100:
    print(price
"""

    tokens, error = analyze_tokens(source_code)

    assert error is not None
    assert error["type"] == "TokenError"
    assert error["line"] is not None