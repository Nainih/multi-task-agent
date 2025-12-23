from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver


class MathState(TypedDict):
    """State for the math agent."""

    expression: str
    result: str


def safe_eval_math(expr: str) -> str:
    """
    Safely evaluate a basic math expression.

    Supports: +, -, *, /, **, parentheses, integers and decimals.
    No variables or function calls are allowed.
    """
    allowed_chars = "0123456789+-*/(). "
    if any(c not in allowed_chars for c in expr):
        return "Error: Only numbers and + - * / ** and parentheses are allowed."

    try:
        # Use a restricted eval environment
        value = eval(expr, {"__builtins__": None}, {})
    except ZeroDivisionError:
        return "Error: Division by zero."
    except Exception as e:
        return f"Error: Could not evaluate expression ({e})."

    return str(value)


def math_node(state: MathState) -> MathState:
    expr = state.get("expression", "").strip()
    if not expr:
        return {"expression": "", "result": "Error: Empty expression."}

    result = safe_eval_math(expr)
    return {"expression": expr, "result": result}


def build_math_app():
    """Build and return a LangGraph app that can evaluate basic math expressions."""
    builder = StateGraph(MathState)
    builder.add_node("math", math_node)

    builder.add_edge(START, "math")
    builder.add_edge("math", END)

    checkpointer = MemorySaver()
    app = builder.compile(checkpointer=checkpointer)
    return app


if __name__ == "__main__":
    app = build_math_app()
    config = {"configurable": {"thread_id": "math-thread-1"}}

    print("Simple Math Agent (type 'quit' to exit)")
    while True:
        expr = input("Enter math expression: ")
        if expr.lower().strip() in {"quit", "exit"}:
            break

        state = {"expression": expr, "result": ""}
        result = app.invoke(state, config=config)
        print("Result:", result.get("result"))



