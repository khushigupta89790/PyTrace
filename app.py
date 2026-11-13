
import html
import streamlit as st
import pandas as pd

from compiler.pipeline import run_pipeline


# =========================================================
# 1. PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="PyTrace | Compiler Workbench",
    page_icon="P",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# 2. DESIGN SYSTEM
# =========================================================

st.markdown("""
<style>

.stApp {
    background: #F4F2EC;
    color: #293A32;
}

.block-container {
    max-width: 1450px;
    padding: 2rem 2rem 3rem 2rem;
}

html, body, [class*="css"] {
    font-family: "Segoe UI", sans-serif;
}

h1, h2, h3, h4 {
    color: #293A32 !important;
    letter-spacing: -0.5px;
}

p, label {
    color: #59665E;
}

section[data-testid="stSidebar"] {
    background: #244B3C !important;
    border-right: 1px solid #1B3D30;
}

section[data-testid="stSidebar"] * {
    color: #F4F5EF !important;
}

section[data-testid="stSidebar"] hr {
    border-color: #527362 !important;
}

section[data-testid="stSidebar"] [data-testid="stRadio"] label {
    padding: 7px 10px;
    border-radius: 7px;
    font-size: 14px;
}

div[data-testid="stButton"] button {
    background: #FFFFFF !important;
    color: #29483D !important;
    border: 1px solid #CFD9D0 !important;
    border-radius: 8px !important;
    min-height: 43px;
    font-weight: 600;
    opacity: 1 !important;
}

div[data-testid="stButton"] button p,
div[data-testid="stButton"] button span {
    color: #29483D !important;
    opacity: 1 !important;
}

div[data-testid="stButton"] button[kind="primary"] {
    background: #356B52 !important;
    color: #FFFFFF !important;
    border: 1px solid #356B52 !important;
}

div[data-testid="stButton"] button[kind="primary"] p,
div[data-testid="stButton"] button[kind="primary"] span {
    color: #FFFFFF !important;
}

div[data-testid="stButton"] button:hover {
    border-color: #6A967B !important;
}

div[data-testid="stButton"] button[kind="primary"]:hover {
    background: #28563F !important;
}

div[data-testid="stTextArea"] textarea {
    background: #FFFFFF !important;
    color: #263B30 !important;
    border: 1px solid #D6DED5 !important;
    border-radius: 9px !important;
    font-family: Consolas, monospace !important;
    font-size: 14px !important;
    line-height: 1.7 !important;
    opacity: 1 !important;
}

div[data-testid="stMetric"] {
    background: #FFFFFF !important;
    border: 1px solid #E0E4DC !important;
    border-radius: 11px !important;
    padding: 17px !important;
    box-shadow: 0 3px 10px rgba(42, 65, 49, 0.045);
}

div[data-testid="stMetricLabel"],
div[data-testid="stMetricLabel"] * {
    color: #68776D !important;
}

div[data-testid="stMetricValue"],
div[data-testid="stMetricValue"] * {
    color: #315C43 !important;
    font-size: 28px !important;
    font-weight: 650 !important;
}

div[data-testid="stDataFrame"] {
    background: #FFFFFF;
    border: 1px solid #E0E4DC;
    border-radius: 9px;
    overflow: hidden;
}

div[data-testid="stCode"] {
    border: 1px solid #E0E4DC;
    border-radius: 9px;
}

div[data-testid="stExpander"] {
    background: #FFFFFF;
    border: 1px solid #E0E4DC;
    border-radius: 9px;
}

hr {
    border-color: #E0E2DA !important;
}

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# 3. REUSABLE VISUAL COMPONENTS
# =========================================================

def render_notice(kind, title, message):

    styles = {
        "success": {
            "background": "#E1EFE5",
            "border": "#A8CDB3",
            "title": "#285B3E",
            "text": "#365E45",
            "icon": "✓"
        },
        "warning": {
            "background": "#F8EEDB",
            "border": "#E5CC96",
            "title": "#805A20",
            "text": "#70552C",
            "icon": "!"
        },
        "error": {
            "background": "#F6E3E2",
            "border": "#E1B2AF",
            "title": "#873F43",
            "text": "#743F42",
            "icon": "×"
        },
        "info": {
            "background": "#E3EDF5",
            "border": "#B4CCDE",
            "title": "#315B78",
            "text": "#405F77",
            "icon": "i"
        }
    }

    style = styles.get(kind, styles["info"])

    safe_title = html.escape(str(title))
    safe_message = html.escape(str(message))

    st.markdown(
        f"""
        <div style="
            background:{style['background']};
            border:1px solid {style['border']};
            border-radius:10px;
            padding:15px 18px;
            margin:10px 0 17px 0;
            display:flex;
            align-items:flex-start;
            gap:13px;
        ">
            <div style="
                width:27px;
                height:27px;
                min-width:27px;
                border-radius:50%;
                background:rgba(255,255,255,0.75);
                color:{style['title']};
                display:flex;
                align-items:center;
                justify-content:center;
                font-weight:700;
                font-size:16px;
            ">
                {style['icon']}
            </div>
            <div>
                <div style="
                    color:{style['title']};
                    font-weight:700;
                    font-size:14px;
                    margin-bottom:3px;
                ">
                    {safe_title}
                </div>
                <div style="
                    color:{style['text']};
                    font-size:13px;
                    line-height:1.55;
                ">
                    {safe_message}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_section_heading(title, subtitle=None):

    safe_title = html.escape(str(title))

    subtitle_html = ""

    if subtitle:
        subtitle_html = (
            f'<p style="color:#7A857C;font-size:13px;'
            f'margin-top:5px;">{html.escape(str(subtitle))}</p>'
        )

    st.markdown(
        f"""
        <div style="margin-bottom:15px;">
            <h3 style="
                color:#293A32;
                font-size:23px;
                margin:0;
            ">{safe_title}</h3>
            {subtitle_html}
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# 4. SAMPLE PROGRAM
# =========================================================

SAMPLE_CODE = """price = 500
quantity = 3

total = price * quantity

print(total)
"""


# =========================================================
# 5. SESSION STATE
# =========================================================

if "source_code" not in st.session_state:
    st.session_state.source_code = SAMPLE_CODE

if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = None

if "analysis_source_code" not in st.session_state:
    st.session_state.analysis_source_code = SAMPLE_CODE


# =========================================================
# 6. SIDEBAR
# =========================================================

results = st.session_state.analysis_results

sections = [
    "Overview",
    "Lexical Analysis",
    "Syntax Analysis",
    "Symbol Table",
    "Semantic Analysis",
    "Intermediate Code",
    "Optimization",
    "Generated Code"
]

if results is not None and results.get("validation") is not None:
    sections.append("Execution Validation")


with st.sidebar:

    st.markdown("""
    <div style="padding:8px 0 12px 0;">
        <div style="
            font-size:29px;
            font-weight:750;
            letter-spacing:-1px;
            color:#FFFFFF;
        ">PyTrace</div>
        <div style="
            color:#B9D0C1;
            font-size:10px;
            letter-spacing:2px;
            margin-top:3px;
        ">PYTHON COMPILER WORKBENCH</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown("##### WORKSPACE")

    section = st.radio(
        "Navigation",
        sections,
        index=0,
        key="pytrace_navigation_v5",
        label_visibility="collapsed"
    )

    st.divider()

    st.markdown("##### ABOUT")

    st.caption(
        "A Python source-code analysis and optimization system."
    )

    st.caption("Version 1.0")

    st.markdown("""
    <div style="
        margin-top:35px;
        padding:12px;
        background:#315B49;
        border-radius:8px;
        color:#DCE9DF;
        font-size:11px;
        line-height:1.6;
    ">
        Built with Python<br>
        Powered by AST and Tokenize
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# 7. MAIN HEADER
# =========================================================

header_left, header_right = st.columns([4, 1])

with header_left:

    st.markdown("""
    <div style="padding-bottom:4px;">
        <h1 style="
            color:#293A32;
            font-size:34px;
            font-weight:750;
            margin:0;
            letter-spacing:-1.2px;
        ">PyTrace</h1>
        <p style="
            color:#788078;
            font-size:13px;
            margin-top:5px;
        ">
            Python Compiler Optimization & Error Investigation System
        </p>
    </div>
    """, unsafe_allow_html=True)

with header_right:

    st.markdown("""
    <div style="
        text-align:right;
        padding-top:12px;
        color:#718078;
        font-size:11px;
        letter-spacing:1px;
    ">
        COMPILER<br>WORKBENCH
    </div>
    """, unsafe_allow_html=True)

st.divider()


# =========================================================
# 8. SOURCE CODE EDITOR
# =========================================================

render_section_heading(
    "Source Code",
    "Write or paste your Python program to begin."
)

editor_col, action_col = st.columns([5, 1])

with editor_col:

    source_code = st.text_area(
        "Python source code",
        key="source_code",
        height=235,
        label_visibility="collapsed",
        placeholder="Write your Python code here..."
    )

with action_col:

    st.markdown(
        "<div style='height:7px'></div>",
        unsafe_allow_html=True
    )

    analyze_button = st.button(
        "Run Analysis",
        type="primary",
        width="stretch"
    )

    reset_button = st.button(
        "Load Sample",
        width="stretch"
    )

    if reset_button:

        st.session_state.source_code = SAMPLE_CODE
        st.session_state.analysis_results = None
        st.session_state.analysis_source_code = SAMPLE_CODE

        st.rerun()


# =========================================================
# 9. RUN PIPELINE
# =========================================================

if analyze_button:

    if not source_code.strip():

        render_notice(
            "warning",
            "Empty source code",
            "Please enter a Python program before running the analysis."
        )

    else:

        with st.spinner(
            "Running compiler stages and execution validation..."
        ):

            try:

                analysis = run_pipeline(
                    source_code,
                    validate=True
                )

                if not isinstance(analysis, dict):
                    raise TypeError(
                        "The compiler pipeline did not return a valid result dictionary."
                    )

                st.session_state.analysis_results = analysis
                st.session_state.analysis_source_code = source_code

            except Exception as error:

                st.session_state.analysis_source_code = source_code

                st.session_state.analysis_results = {
                    "status": "APPLICATION_ERROR",
                    "error": str(error),
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


# Refresh results after execution

results = st.session_state.analysis_results
analysis_source = st.session_state.analysis_source_code


# =========================================================
# 10. EMPTY WORKSPACE OR RESULTS
# =========================================================

if results is None:

    st.html("""
    <div style="
        background:#FFFFFF;
        border:1px solid #E2E5DD;
        border-radius:12px;
        padding:27px;
        margin-top:12px;
    ">

        <div style="
            color:#315C43;
            font-size:12px;
            font-weight:700;
            letter-spacing:1px;
        ">
            YOUR WORKSPACE
        </div>

        <h3 style="
            color:#293A32;
            margin-top:10px;
            font-size:23px;
        ">
            Ready when you are.
        </h3>

        <p style="
            color:#788078;
            font-size:14px;
            line-height:1.7;
        ">
            Enter a Python program above and run the analysis.
            PyTrace will inspect the code, build its intermediate
            representation, apply optimizations and compare outputs.
        </p>

        <div style="
            display:flex;
            flex-wrap:wrap;
            gap:9px;
            margin-top:18px;
        ">

            <span style="
                background:#E1EDE5;
                color:#315C43;
                padding:7px 12px;
                border-radius:6px;
                font-size:12px;
            ">Lexical Analysis</span>

            <span style="
                background:#E8E5F4;
                color:#62538A;
                padding:7px 12px;
                border-radius:6px;
                font-size:12px;
            ">Syntax Analysis</span>

            <span style="
                background:#F7E8DC;
                color:#945B37;
                padding:7px 12px;
                border-radius:6px;
                font-size:12px;
            ">Semantic Checks</span>

            <span style="
                background:#DFEAF3;
                color:#37698C;
                padding:7px 12px;
                border-radius:6px;
                font-size:12px;
            ">Optimization</span>

        </div>

    </div>
    """)


else:

    # All result-related code is safely inside this ELSE block.
    # This ensures results is never None when .get() is used.

    status = results.get("status", "UNKNOWN")

    st.divider()


    # =====================================================
    # 11. OVERVIEW
    # =====================================================

    if section == "Overview":

        render_section_heading(
            "Analysis Overview",
            "A summary of the latest compiler run."
        )

        if status == "COMPLETED":

            render_notice(
                "success",
                "Analysis completed successfully",
                "The compiler pipeline finished processing your Python program."
            )

        elif status == "SEMANTIC_ISSUES":

            render_notice(
                "warning",
                "Semantic issues detected",
                "Review the semantic analysis section for details."
            )

        elif status in ("LEXICAL_ERROR", "SYNTAX_ERROR"):

            render_notice(
                "error",
                f"Analysis stopped: {status}",
                str(results.get("error", "An analysis error occurred."))
            )

        else:

            render_notice(
                "info",
                f"Pipeline status: {status}",
                str(results.get("error", "Check the individual compiler stages."))
            )

        if results.get("error") and status not in (
            "LEXICAL_ERROR",
            "SYNTAX_ERROR",
            "APPLICATION_ERROR"
        ):

            st.code(str(results["error"]), language="text")

        # Metrics

        m1, m2, m3, m4 = st.columns(4)

        with m1:
            st.metric("Tokens", len(results.get("tokens") or []))

        with m2:
            st.metric("AST Nodes", len(results.get("ast") or []))

        with m3:
            st.metric("Symbols", len(results.get("symbol_table") or []))

        with m4:
            st.metric("Optimizations", len(results.get("optimizations") or []))

        # Optimized result

        render_section_heading(
            "Optimization Result",
            "Original source compared with optimized Python code."
        )

        optimized_code = results.get("optimized_code")

        if optimized_code is not None:

            original_col, optimized_col = st.columns(2)

            with original_col:

                st.markdown("""
                <div style="
                    background:#E8E5F4;
                    color:#62538A;
                    padding:8px 12px;
                    border-radius:7px 7px 0 0;
                    font-size:12px;
                    font-weight:700;
                ">
                    ORIGINAL PROGRAM
                </div>
                """, unsafe_allow_html=True)

                st.code(analysis_source, language="python")

            with optimized_col:

                st.markdown("""
                <div style="
                    background:#E1EDE5;
                    color:#315C43;
                    padding:8px 12px;
                    border-radius:7px 7px 0 0;
                    font-size:12px;
                    font-weight:700;
                ">
                    OPTIMIZED PROGRAM
                </div>
                """, unsafe_allow_html=True)

                st.code(optimized_code, language="python")

        # Pipeline stage summary

        render_section_heading("Compiler Stages")

        stages = [
            ("Lexical Analysis", bool(results.get("tokens"))),
            ("Syntax Analysis", bool(results.get("ast"))),
            ("Symbol Table", bool(results.get("symbol_table"))),
            ("Semantic Analysis", bool(results.get("semantic"))),
            ("Intermediate Code", bool(results.get("intermediate_code"))),
            ("Optimization", optimized_code is not None),
            ("Code Generation", results.get("generated_code") is not None)
        ]

        for name, completed in stages:

            color = "#DCEDE1" if completed else "#F0E8D8"
            text_color = "#315C43" if completed else "#86672F"
            label = "Complete" if completed else "Unavailable"

            st.markdown(
                f"""
                <div style="
                    display:flex;
                    justify-content:space-between;
                    align-items:center;
                    padding:10px 13px;
                    background:#FFFFFF;
                    border:1px solid #E5E7E0;
                    border-radius:7px;
                    margin-bottom:7px;
                ">
                    <span style="
                        color:#35463C;
                        font-size:13px;
                        font-weight:600;
                    ">
                        {html.escape(name)}
                    </span>
                    <span style="
                        background:{color};
                        color:{text_color};
                        border-radius:20px;
                        padding:4px 10px;
                        font-size:11px;
                        font-weight:700;
                    ">
                        {label}
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )

        if results.get("intermediate_error"):

            render_notice(
                "warning",
                "Intermediate code limitation",
                results["intermediate_error"]
            )

        # Validation summary

        validation = results.get("validation")

        if validation is not None:

            render_section_heading("Execution Validation")

            if validation.get("status") == "PASSED":

                render_notice(
                    "success",
                    "Validation passed",
                    "The original and optimized programs produced matching standard output."
                )

            else:

                render_notice(
                    "warning",
                    "Validation needs attention",
                    f"Validation status: {validation.get('status')}"
                )


    # =====================================================
    # 12. LEXICAL ANALYSIS
    # =====================================================

    elif section == "Lexical Analysis":

        render_section_heading(
            "Lexical Analysis",
            "Tokens identified in the Python source program."
        )

        tokens = results.get("tokens") or []

        if tokens:

            st.metric("Total Tokens", len(tokens))

            st.dataframe(
                pd.DataFrame(tokens),
                width="stretch",
                hide_index=True
            )

        else:

            render_notice(
                "info",
                "No tokens available",
                "The lexer did not return any token information."
            )


    # =====================================================
    # 13. SYNTAX ANALYSIS
    # =====================================================

    elif section == "Syntax Analysis":

        render_section_heading(
            "Syntax Analysis",
            "Abstract Syntax Tree node information."
        )

        ast_nodes = results.get("ast") or []

        if ast_nodes:

            st.metric("Total AST Nodes", len(ast_nodes))

            render_section_heading(
                "AST Node Summary",
                "Distribution of different node types in the program."
            )

            ast_df = pd.DataFrame(ast_nodes)

            if "node_type" in ast_df.columns:

                node_summary = (
                    ast_df["node_type"]
                    .value_counts()
                    .rename_axis("Node Type")
                    .reset_index(name="Count")
                )

                summary_col, chart_col = st.columns([3, 2])

                with summary_col:

                    st.dataframe(
                        node_summary,
                        width="stretch",
                        hide_index=True
                    )

                with chart_col:

                    st.bar_chart(
                        node_summary.set_index("Node Type"),
                        horizontal=True
                    )

            render_section_heading(
                "AST Node Details",
                "Node types and their source-code locations."
            )

            st.dataframe(
                ast_df,
                width="stretch",
                hide_index=True
            )

        else:

            render_notice(
                "info",
                "AST unavailable",
                "No abstract syntax tree information was generated."
            )


    # =====================================================
    # 14. SYMBOL TABLE
    # =====================================================

    elif section == "Symbol Table":

        render_section_heading(
            "Symbol Table",
            "Identifiers, inferred data types, scopes and references."
        )

        symbols = results.get("symbol_table") or []

        if symbols:

            st.dataframe(
                pd.DataFrame(symbols),
                width="stretch",
                hide_index=True
            )

        else:

            render_notice(
                "info",
                "No symbols found",
                "No symbol entries were returned for this program."
            )


    # =====================================================
    # 15. SEMANTIC ANALYSIS
    # =====================================================

    elif section == "Semantic Analysis":

        render_section_heading(
            "Semantic Analysis",
            "Review undefined variables and other supported diagnostics."
        )

        semantic = results.get("semantic") or {}

        c1, c2 = st.columns(2)

        with c1:

            st.metric(
                "Errors",
                semantic.get("total_errors", 0)
            )

        with c2:

            st.metric(
                "Warnings",
                semantic.get("total_warnings", 0)
            )

        st.markdown("### Errors")

        errors = semantic.get("errors") or []

        if errors:

            st.dataframe(
                pd.DataFrame(errors),
                width="stretch",
                hide_index=True
            )

        else:

            render_notice(
                "success",
                "No semantic errors",
                "No semantic errors were detected by the current analyzer."
            )

        st.markdown("### Warnings")

        warnings = semantic.get("warnings") or []

        if warnings:

            st.dataframe(
                pd.DataFrame(warnings),
                width="stretch",
                hide_index=True
            )

        else:

            render_notice(
                "info",
                "No semantic warnings",
                "No semantic warnings were reported for this program."
            )


    # =====================================================
    # 16. INTERMEDIATE CODE
    # =====================================================

    elif section == "Intermediate Code":

        render_section_heading(
            "Intermediate Code",
            "Three-address instructions and control-flow representation."
        )

        instructions = results.get("intermediate_code") or []

        if instructions:

            st.code(
                "\n".join(instructions),
                language="text"
            )

            st.caption(
                f"{len(instructions)} intermediate instructions generated."
            )

        else:

            render_notice(
                "info",
                "No intermediate code",
                "No intermediate instructions were generated."
            )

        if results.get("intermediate_error"):

            render_notice(
                "warning",
                "Unsupported construct",
                results["intermediate_error"]
            )


    # =====================================================
    # 17. OPTIMIZATION
    # =====================================================

    elif section == "Optimization":

        render_section_heading(
            "Code Optimization",
            "Compare the original program with the optimized version."
        )

        optimized_code = results.get("optimized_code")

        if optimized_code is not None:

            original_col, optimized_col = st.columns(2)

            with original_col:

                st.markdown("""
                <div style="
                    background:#E8E5F4;
                    color:#62538A;
                    padding:9px 12px;
                    border-radius:8px 8px 0 0;
                    font-weight:700;
                    font-size:12px;
                ">
                    ORIGINAL CODE
                </div>
                """, unsafe_allow_html=True)

                st.code(analysis_source, language="python")

            with optimized_col:

                st.markdown("""
                <div style="
                    background:#E1EDE5;
                    color:#315C43;
                    padding:9px 12px;
                    border-radius:8px 8px 0 0;
                    font-weight:700;
                    font-size:12px;
                ">
                    OPTIMIZED CODE
                </div>
                """, unsafe_allow_html=True)

                st.code(optimized_code, language="python")

            render_section_heading("Optimization Details")

            optimizations = results.get("optimizations") or []

            if optimizations:

                st.dataframe(
                    pd.DataFrame(optimizations),
                    width="stretch",
                    hide_index=True
                )

                st.caption(
                    f"{len(optimizations)} transformations recorded."
                )

            else:

                render_notice(
                    "info",
                    "No transformations applied",
                    "The optimizer did not find any supported transformations."
                )

        else:

            render_notice(
                "info",
                "Optimized code unavailable",
                "Optimization was not completed for this program."
            )


    # =====================================================
    # 18. GENERATED CODE
    # =====================================================

    elif section == "Generated Code":

        render_section_heading(
            "Generated Python Code",
            "Python source reconstructed from the optimized syntax tree."
        )

        generated_code = results.get("generated_code")

        if generated_code is not None:

            st.code(
                generated_code,
                language="python"
            )

        else:

            render_notice(
                "info",
                "Generated code unavailable",
                "The code generation stage did not produce output."
            )


    # =====================================================
    # 19. EXECUTION VALIDATION
    # =====================================================

    elif section == "Execution Validation":

        render_section_heading(
            "Execution Validation",
            "Compare captured standard output from both programs."
        )

        validation = results.get("validation")

        if validation is None:

            render_notice(
                "warning",
                "Validation unavailable",
                "The pipeline did not return an execution validation result."
            )

        else:

            validation_status = validation.get("status")

            if validation_status == "PASSED":

                render_notice(
                    "success",
                    "Validation passed",
                    "The original and optimized programs produced matching standard output."
                )

            elif validation_status == "FAILED":

                render_notice(
                    "error",
                    "Output mismatch",
                    "The original and optimized programs produced different standard output."
                )

            elif validation_status == "ORIGINAL_EXECUTION_FAILED":

                render_notice(
                    "error",
                    "Original execution failed",
                    "The original program could not complete successfully."
                )

            elif validation_status == "OPTIMIZED_EXECUTION_FAILED":

                render_notice(
                    "error",
                    "Optimized execution failed",
                    "The optimized program could not complete successfully."
                )

            else:

                render_notice(
                    "warning",
                    "Validation status",
                    str(validation_status)
                )

            render_section_heading("Output Comparison")

            original_col, optimized_col = st.columns(2)

            with original_col:

                st.markdown("""
                <div style="
                    background:#E8E5F4;
                    color:#62538A;
                    padding:9px 12px;
                    border-radius:8px 8px 0 0;
                    font-weight:700;
                    font-size:12px;
                ">
                    ORIGINAL OUTPUT
                </div>
                """, unsafe_allow_html=True)

                st.code(
                    validation.get("original_output", "") or "(No output)",
                    language="text"
                )

                if validation.get("original_error"):

                    st.caption("Original execution error")

                    st.code(
                        validation["original_error"],
                        language="text"
                    )

            with optimized_col:

                st.markdown("""
                <div style="
                    background:#E1EDE5;
                    color:#315C43;
                    padding:9px 12px;
                    border-radius:8px 8px 0 0;
                    font-weight:700;
                    font-size:12px;
                ">
                    OPTIMIZED OUTPUT
                </div>
                """, unsafe_allow_html=True)

                st.code(
                    validation.get("optimized_output", "") or "(No output)",
                    language="text"
                )

                if validation.get("optimized_error"):

                    st.caption("Optimized execution error")

                    st.code(
                        validation["optimized_error"],
                        language="text"
                    )

            matches = validation.get("outputs_match", False)

            render_notice(
                "success" if matches else "warning",
                "Outputs match" if matches else "Outputs do not match",
                "Captured standard output comparison: "
                + ("True" if matches else "False")
            )

            st.caption(
                "This validator compares captured standard output. "
                "It does not prove equivalence of all side effects or "
                "provide a secure sandbox for arbitrary code."
            )


# =========================================================
# 20. FOOTER
# =========================================================

st.divider()

st.markdown("""
<div style="
    text-align:center;
    padding:12px 0;
    color:#879188;
    font-size:12px;
">
    PyTrace &nbsp;·&nbsp; Python Compiler Workbench
    &nbsp;·&nbsp; Built with Python
</div>
""", unsafe_allow_html=True)
