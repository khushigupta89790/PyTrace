# PyTrace – Python Compiler Optimization & Error Investigation System

**PyTrace** is a Python-based compiler analysis and optimization system designed to examine Python source code through multiple stages of compilation. It provides lexical analysis, syntax analysis, symbol table construction, semantic analysis, intermediate code generation, code optimization, and execution validation through an interactive Streamlit interface.

The project demonstrates fundamental compiler design concepts using Python's built-in parsing capabilities and custom analysis and optimization logic.

---

## 1. Project Overview

PyTrace analyzes Python source code and presents the results of different compiler stages in an interactive developer workbench.

The system helps users understand how source code is processed, identify potential programming errors, inspect intermediate representations, and observe code optimization techniques.

## 2. Key Features

- **Lexical Analysis:** Identifies and classifies tokens such as keywords, identifiers, operators, constants, and literals.
- **Syntax Analysis:** Parses Python source code and generates an Abstract Syntax Tree (AST).
- **AST Analysis:** Examines AST nodes and provides node summaries and structural information.
- **Symbol Table Management:** Tracks variables, functions, parameters, data types, assignments, references, and scopes.
- **Semantic Analysis:** Detects issues such as undefined variables and identifies warnings such as unused variables and multiple assignments.
- **Intermediate Code Generation:** Converts supported Python constructs into an intermediate, three-address-style representation.
- **Code Optimization:** Implements optimization techniques including constant folding, constant propagation, and dead code elimination.
- **Code Generation:** Generates Python source code from the optimized AST.
- **Execution Validation:** Compares the standard output of original and optimized programs to check whether their outputs match.
- **Interactive Dashboard:** Provides a Streamlit-based interface to explore the different stages of analysis.

## 3. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Streamlit | Interactive frontend |
| AST | Syntax tree generation and analysis |
| Tokenize | Lexical analysis |
| Pandas | Tabular presentation of results |
| Pytest | Automated testing |

## 4. System Architecture

PyTrace follows a sequential compiler analysis pipeline.

1. Source Code Input
2. Lexical Analysis
3. Syntax Analysis
4. AST Analysis
5. Symbol Table Construction
6. Semantic Analysis
7. Intermediate Code Generation
8. Code Optimization
9. Python Code Generation
10. Execution Validation

Each stage contributes to analyzing, transforming, or validating the source program.

## 5. Project Structure

```text
PyTrace/
│
├── compiler/
│   ├── __init__.py
│   ├── lexer.py
│   ├── parser.py
│   ├── symbol_table.py
│   ├── semantic.py
│   ├── intermediate.py
│   ├── optimizer.py
│   ├── code_generator.py
│   ├── validator.py
│   └── pipeline.py
│
├── samples/
│   └── sample.py
│
├── tests/
│   ├── test_lexer.py
│   ├── test_parser.py
│   ├── test_symbol_table.py
│   ├── test_semantic.py
│   ├── test_intermediate.py
│   ├── test_optimizer.py
│   ├── test_code_generator.py
│   ├── test_validator.py
│   └── test_pipeline.py
│
├── app.py
├── requirements.txt
├── README.md
└── .gitignore
```

## 6. Installation and Setup

### Prerequisites

- Python 3.10 or later
- pip
- Git (optional)

### Step 1: Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd PyTrace
```

Replace the placeholder with your actual GitHub repository URL.

### Step 2: Create a virtual environment

**Windows:**

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\activate
```

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

## 7. Running the Application

Start the Streamlit application using:

```bash
streamlit run app.py
```

Open the local URL displayed in your terminal, usually:

```text
http://localhost:8501
```

Enter Python source code in the editor and select **Run Analysis** to explore the compiler pipeline results.

A sample program is also available in the `samples/` directory.

## 8. Running Automated Tests

PyTrace includes an automated test suite implemented using Pytest.

To run all tests:

```bash
python -m pytest tests -v
```

The test suite covers:

- Lexical analysis
- Syntax analysis
- Symbol table construction
- Semantic analysis
- Intermediate code generation
- Code optimization
- Code generation
- Execution validation
- Complete pipeline integration

**Current test results:** 48 tests passed.

## 9. Current Limitations

PyTrace is an educational compiler analysis and optimization system, not a complete implementation of the Python language compiler.

- Intermediate code generation supports selected Python constructs; unsupported expressions may raise an explicit error.
- Semantic analysis implements selected static checks and does not provide complete Python scope or control-flow analysis.
- Optimization is conservative and does not cover every Python construct or execution scenario.
- Execution validation compares standard output and does not establish equivalence of all program behaviour.
- The execution validator uses subprocess execution with a timeout; it is not a secure sandbox. Only trusted source code should be executed.

## 10. Future Enhancements

- Expand support for additional Python syntax and expressions.
- Improve semantic analysis and scope handling.
- Extend intermediate representation and optimization techniques.
- Improve optimization safety for more complex control-flow structures.
- Add richer compiler diagnostics and debugging information.
- Introduce more comprehensive execution and equivalence testing.

## 11. Learning Outcomes

This project demonstrates practical implementation of compiler design concepts, including lexical analysis, parsing, AST traversal, symbol table construction, semantic checks, intermediate representation, optimization, code generation, and software testing.

It also demonstrates the integration of a Python backend with an interactive Streamlit frontend.

---

**Project:** PyTrace – Python Compiler Optimization & Error Investigation System

**Developed using:** Python, Streamlit, Pandas, and Pytest.