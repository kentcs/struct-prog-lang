"""
Simple error reporting module for the Trivial language interpreter.
"""


def error(explanation, line=None, column=None, exit=True):
    """
    Report an error with optional location information.

    Args:
        explanation: Error message string
        line: Line number (optional)
        column: Column number (optional)
        exit: Whether to raise an exception (default True)

    Raises:
        Exception with formatted error message if exit=True
    """
    parts = ["Error"]

    # Add location information if available
    location_parts = []
    if line is not None:
        location_parts.append(f"line {line}")
    if column is not None:
        location_parts.append(f"column {column}")

    if location_parts:
        parts.append(f"at {', '.join(location_parts)}")

    parts.append(f": {explanation}")

    message = " ".join(parts)

    if exit:
        raise Exception(message)
    else:
        print(message)


def check(condition, explanation, line=None, column=None, exit=True):
    """
    Assert a condition and report an error if false.

    Args:
        condition: Boolean condition to check
        explanation: Error message if condition is false
        line: Line number (optional)
        column: Column number (optional)
        exit: Whether to raise an exception (default True)
    """
    if not condition:
        error(explanation, line=line, column=column, exit=exit)
