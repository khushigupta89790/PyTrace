
import builtins
import tokenize
import io
import keyword
import token


def classify_token(tok):
    """Classify Python tokens into meaningful categories."""

    token_type = tok.type
    value = tok.string

    if token_type == token.NAME:

        if keyword.iskeyword(value):
            return "KEYWORD"

        elif value in ("True", "False", "None"):
            return "CONSTANT"

        elif hasattr(builtins, value) and callable(
            getattr(builtins, value)
        ):
            return "BUILTIN_FUNCTION"

        elif hasattr(builtins, value):
            return "BUILTIN"

        return "IDENTIFIER"

    elif token_type == token.NUMBER:
        return "NUMBER"

    elif token_type == token.STRING:
        return "STRING"

    elif token_type == token.OP:

        if value in "(){}[]":
            return "BRACKET"

        elif value in ",:;.":
            return "DELIMITER"

        elif value in (
            "+", "-", "*", "/", "//", "%", "**",
            "@", "<<", ">>", "&", "|", "^", "~",
            ":=", "=", "+=", "-=", "*=", "/=",
            "//=", "%=", "**=", "&=", "|=", "^=",
            ">>=", "<<=", "@="
        ):
            return "OPERATOR"

        elif value in (
            "==", "!=", "<", ">", "<=", ">="
        ):
            return "COMPARISON_OPERATOR"

        else:
            return "OTHER_OPERATOR"

    elif token_type == token.COMMENT:
        return "COMMENT"

    elif token_type == token.INDENT:
        return "INDENTATION"

    elif token_type == token.DEDENT:
        return "DEDENT"

    elif token_type in (token.NEWLINE, tokenize.NL):
        return "NEWLINE"

    elif token_type == token.ERRORTOKEN:
        return "ERROR"

    elif token_type == token.ENDMARKER:
        return "ENDMARKER"

    return "OTHER"


def analyze_tokens(source_code):
    """Perform lexical analysis on Python source code."""

    tokens_found = []

    try:

        generator = tokenize.generate_tokens(
            io.StringIO(source_code).readline
        )

        for tok in generator:

            # Ignore empty end markers and blank logical lines.
            if tok.type == token.ENDMARKER and not tok.string:
                continue

            if tok.type == tokenize.NL and not tok.string.strip():
                continue

            if tok.type == token.NEWLINE and not tok.string.strip():
                continue

            tokens_found.append({
                "lexeme": tok.string,
                "token_type": classify_token(tok),
                "line": tok.start[0],
                "column": tok.start[1],
                "end_line": tok.end[0],
                "end_column": tok.end[1]
            })

        return tokens_found, None

    except (tokenize.TokenError, IndentationError, SyntaxError) as error:

        error_details = {
            "type": type(error).__name__,
            "message": str(error),
            "line": None,
            "column": None
        }

        if isinstance(error, tokenize.TokenError):
            position = error.args[1]

            if position:
                error_details["line"] = position[0]
                error_details["column"] = position[1]

        elif isinstance(error, IndentationError):
            error_details["line"] = error.lineno
            error_details["column"] = error.offset

        elif isinstance(error, SyntaxError):
            error_details["line"] = error.lineno
            error_details["column"] = error.offset

        return tokens_found, error_details
