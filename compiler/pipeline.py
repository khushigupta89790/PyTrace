
import ast

from compiler.lexer import analyze_tokens
from compiler.parser import parse_source, analyze_ast
from compiler.symbol_table import build_symbol_table
from compiler.semantic import analyze_semantics
from compiler.intermediate import generate_intermediate_code
from compiler.optimizer import optimize_code
from compiler.code_generator import generate_from_ast
from compiler.validator import validate_optimization


def run_pipeline(source_code, validate=False):
    """
    Run the complete PyTrace analysis and optimization pipeline.

    Set validate=True only for trusted source code.
    """

    results = {
        "status": "STARTED",
        "tokens": [],
        "ast": [],
        "symbol_table": [],
        "semantic": {},
        "intermediate_code": [],
        "intermediate_error": None,
        "optimized_code": None,
        "optimizations": [],
        "generated_code": None,
        "validation": None
    }

    # Stage 1: Lexical Analysis
    tokens, lexical_error = analyze_tokens(source_code)
    results["tokens"] = tokens

    if lexical_error:
        results["status"] = "LEXICAL_ERROR"
        results["error"] = lexical_error
        return results

    # Stage 2: Syntax Analysis
    parsing_result = parse_source(source_code)

    if not parsing_result["success"]:
        results["status"] = "SYNTAX_ERROR"
        results["error"] = parsing_result["error"]
        return results

    syntax_tree = parsing_result["tree"]

    results["ast"] = analyze_ast(syntax_tree)

    # Stage 3: Symbol Table Construction
    results["symbol_table"] = build_symbol_table(source_code)

    # Stage 4: Semantic Analysis
    semantic_result = analyze_semantics(source_code)
    results["semantic"] = semantic_result

    if semantic_result["total_errors"] > 0:
        results["status"] = "SEMANTIC_ISSUES"
        return results

    # Stage 5: Intermediate Code Generation
    try:
        results["intermediate_code"] = (
            generate_intermediate_code(source_code)
        )

    except NotImplementedError as error:
        results["intermediate_error"] = str(error)

    # Stage 6: Code Optimization
    try:
        optimization_result = optimize_code(source_code)

        results["optimized_code"] = (
            optimization_result["optimized_code"]
        )

        results["optimizations"] = (
            optimization_result["optimizations"]
        )

    except (NotImplementedError, TypeError, ValueError) as error:
        results["status"] = "OPTIMIZATION_ERROR"
        results["error"] = str(error)
        return results

    # Stage 7: Optimized Python Code Generation
    try:
        optimized_tree = ast.parse(results["optimized_code"])

        results["generated_code"] = generate_from_ast(
            optimized_tree
        )

    except (SyntaxError, TypeError, ValueError) as error:
        results["status"] = "CODE_GENERATION_ERROR"
        results["error"] = str(error)
        return results

    # Stage 8: Optional Output Validation
    if validate:
        results["validation"] = validate_optimization(
            source_code,
            results["optimized_code"]
        )

    results["status"] = "COMPLETED"

    return results
