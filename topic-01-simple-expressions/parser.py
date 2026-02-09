# parser.py

from tokenizer import tokenize
from pprint import pprint

# EBNF

#   expression = term { ("+" | "-") term }
#   term = factor { ("*" | "/") factor }
#   factor = <number>


def parse_factor(tokens):
    """factor = <number>"""
    token = tokens[0]
    if token["tag"] == "number":
        node = {"tag": "number", "value": token["value"]}
        return node, tokens[1:]
    assert False, f"Expected number, got {token}"


def test_parse_factor():
    """factor = <number>"""
    print("test parse_factor()")
    tokens = tokenize("3")
    ast, tokens = parse_factor(tokens)
    assert ast == {"tag": "number", "value": 3}
    assert tokens == [{"tag": None, "line": 1, "column": 2}]


def parse_term(tokens):
    """term = factor { ("*" | "/") factor }"""
    left, tokens = parse_factor(tokens)
    while tokens[0]["tag"] in ["*", "/"]:
        op = tokens[0]["tag"]
        right, tokens = parse_factor(tokens[1:])
        left = {"tag": op, "left": left, "right": right}
    return left, tokens


def test_parse_term():
    """term = factor { ("*" | "/") factor }"""
    print("test parse_term()")
    tokens = tokenize("3")
    ast, tokens = parse_term(tokens)
    assert ast == {"tag": "number", "value": 3}
    assert tokens == [{"tag": None, "line": 1, "column": 2}]
    tokens = tokenize("3*4")
    ast, tokens = parse_term(tokens)
    assert ast == {
        "left": {"tag": "number", "value": 3},
        "right": {"tag": "number", "value": 4},
        "tag": "*",
    }
    assert tokens == [{"column": 4, "line": 1, "tag": None}]
    tokens = tokenize("3/4")
    ast, tokens = parse_term(tokens)
    assert ast == {
        "left": {"tag": "number", "value": 3},
        "right": {"tag": "number", "value": 4},
        "tag": "/",
    }
    assert tokens == [{"column": 4, "line": 1, "tag": None}]
    tokens = tokenize("3/4*5")
    ast, tokens = parse_term(tokens)
    assert ast == {
        "left": {
            "left": {"tag": "number", "value": 3},
            "right": {"tag": "number", "value": 4},
            "tag": "/",
        },
        "right": {"tag": "number", "value": 5},
        "tag": "*",
    }
    assert tokens == [{"column": 6, "line": 1, "tag": None}]


def parse_expression(tokens):
    """expression = term { ("+" | "-") term }"""
    left, tokens = parse_term(tokens)
    while tokens[0]["tag"] in ["+", "-"]:
        op = tokens[0]["tag"]
        right, tokens = parse_term(tokens[1:])
        left = {"tag": op, "left": left, "right": right}
    return left, tokens


def test_parse_expression():
    """expression = term { ("+" | "-") term }"""
    print("test parse_expression()")
    tokens = tokenize("3")
    ast, tokens = parse_expression(tokens)
    assert ast == {"tag": "number", "value": 3}
    assert tokens == [{"tag": None, "line": 1, "column": 2}]
    tokens = tokenize("3*4+5-6")
    ast, tokens = parse_expression(tokens)
    assert ast == {
        "left": {
            "left": {
                "left": {"tag": "number", "value": 3},
                "right": {"tag": "number", "value": 4},
                "tag": "*",
            },
            "right": {"tag": "number", "value": 5},
            "tag": "+",
        },
        "right": {"tag": "number", "value": 6},
        "tag": "-",
    }
    assert tokens == [{"column": 8, "line": 1, "tag": None}]

def parse(tokens):
    ast, tokens = parse_expression(tokens)
    if tokens[0]["tag"] is not None:
        raise SyntaxError(f"Unexpected token: {tokens[0]}")
    return ast

if __name__ == "__main__":
    test_parse_factor()
    test_parse_term()
    test_parse_expression()
    print("done.")
