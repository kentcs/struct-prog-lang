# parser.py

from tokenizer import tokenize
from pprint import pprint

# EBNF

#   program = statement_list
#   statement_list = { ";" } [ statement { ";" { ";" } statement } ] { ";" }
#   block = "{" statement_list "}"
#   if_statement = "if" "(" expression ")" block [ "else" block ]
#   while_statement = "while" "(" expression ")" block
#   print_statement = "print" expression
#   assignment_statement = <identifier> "=" expression
#   statement = print_statement | assignment_statement

#   expression = term { ("+" | "-") term }
#   term = factor { ("*" | "/") factor }
#   factor = <number> | <identifier> | "(" expression ")"


def parse_factor(tokens):
    # factor = <number> | <identifier> | "(" expression ")"
    token = tokens[0]
    if token["tag"] == "number":
        node = {"tag": "number", "value": token["value"]}
        return node, tokens[1:]
    if token["tag"] == "identifier":
        node = {"tag": "identifier", "value": token["value"]}
        return node, tokens[1:]
    if token["tag"] == "(":
        node, tokens = parse_expression(tokens[1:])
        if tokens[0]["tag"] != ")":
            raise SyntaxError(f"Expected ')', got {tokens[0]}")
        return node, tokens[1:]
    raise SyntaxError(f"Expected factor, got {tokens[0]}")


def test_parse_factor():
    """factor = <number>"""
    print("test parse_factor()")
    tokens = tokenize("3")
    ast, tokens = parse_factor(tokens)
    assert ast == {"tag": "number", "value": 3}
    assert tokens == [{"tag": None, "line": 1, "column": 2}]
    tokens = tokenize("(3+4)")
    ast, tokens = parse_factor(tokens)
    assert ast == {
        "tag": "+",
        "left": {"tag": "number", "value": 3},
        "right": {"tag": "number", "value": 4},
    }
    assert tokens == [{"tag": None, "line": 1, "column": 6}]
    tokens = tokenize("(x+4)")
    ast, tokens = parse_factor(tokens)
    assert ast == {
        "tag": "+",
        "left": {"tag": "identifier", "value": "x"},
        "right": {"tag": "number", "value": 4},
    }
    assert tokens[0]["tag"] == None


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


def parse_print_statement(tokens):
    # print_statement = "print" expression
    assert tokens[0]["tag"] == "print", "Expected 'print'"
    tokens = tokens[1:]
    ast, tokens = parse_expression(tokens)
    return {"tag": "print", "expression": ast}, tokens


def test_parse_print_statement():
    print("test parse_print_statement()")
    tokens = tokenize("print 1")
    ast, tokens = parse_print_statement(tokens)
    assert ast == {"tag": "print", "expression": {"tag": "number", "value": 1}}
    assert tokens[0]["tag"] == None
    tokens = tokenize("print 1+1*3")
    ast, tokens = parse_print_statement(tokens)
    assert tokens[0]["tag"] == None


def parse_assignment_statement(tokens):
    # assignment_statement = <identifier> "=" expression
    assert tokens[0]["tag"] == "identifier", "Expected <identifier>"
    identifier = tokens[0]["value"]
    tokens = tokens[1:]
    assert tokens[0]["tag"] == "=", "Expected '=' fpr assignment"
    tokens = tokens[1:]
    ast, tokens = parse_expression(tokens)
    return {"tag": "assign", "target": identifier, "expression": ast}, tokens


def test_parse_assignment_statement():
    print("test parse_assignment_statement()")
    tokens = tokenize("x = 1")
    ast, tokens = parse_assignment_statement(tokens)
    assert ast == {
        "tag": "assign",
        "target": "x",
        "expression": {"tag": "number", "value": 1},
    }
    assert tokens[0]["tag"] == None
    tokens = tokenize("x = 1+1*3")
    ast, tokens = parse_assignment_statement(tokens)
    assert tokens[0]["tag"] == None


def parse_statement(tokens):
    # statement = print_statement | assignment_statement
    if tokens[0]["tag"] == "print":
        return parse_print_statement(tokens)
    if tokens[0]["tag"] == "identifier":
        return parse_assignment_statement(tokens)
    raise SyntaxError(f"Expected statement, got {tokens[0]}")


def test_parse_statement():
    print("test parse_statement()")
    tokens = tokenize("x = 1")
    ast1, _ = parse_statement(tokens)
    ast2, _ = parse_assignment_statement(tokens)
    assert ast1 == ast2
    tokens = tokenize("print 1")
    ast1, _ = parse_statement(tokens)
    ast2, _ = parse_print_statement(tokens)
    assert ast1 == ast2
    tokens = tokenize("x = 1")
    assert parse_statement(tokens) == parse_assignment_statement(tokens)


def parse_statement_list(tokens):
    # statement_list = { ";" } [ statement { ";" { ";" } statement } ] { ";" }
    statements = []

    # leading semicolons
    while tokens[0]["tag"] == ";":
        tokens = tokens[1:]

    # empty list allowed
    if tokens[0]["tag"] in [None, "}"]:
        return statements, tokens

    # first statement
    statement, tokens = parse_statement(tokens)
    statements.append(statement)

    while True:
        # require at least one semicolon to start another statement
        if tokens[0]["tag"] != ";":
            break

        # consume one-or-more semicolons
        while tokens[0]["tag"] == ";":
            tokens = tokens[1:]

        # trailing semicolons allowed
        if tokens[0]["tag"] in [None, "}"]:
            break

        statement, tokens = parse_statement(tokens)
        statements.append(statement)

    return statements, tokens


def test_parse_statement_list():
    print("test parse_statement_list()")

    # empty input
    tokens = tokenize("")
    statements, rest = parse_statement_list(tokens)
    assert statements == []
    assert rest[0]["tag"] is None

    # only semicolons -> empty list
    tokens = tokenize(";;;")
    statements, rest = parse_statement_list(tokens)
    assert statements == []
    assert rest[0]["tag"] is None

    # single statement, no semicolon
    tokens = tokenize("x=3")
    statements, rest = parse_statement_list(tokens)
    assert len(statements) == 1
    assert statements[0]["tag"] == "assign"
    assert statements[0]["target"] == "x"
    assert rest[0]["tag"] is None

    # single statement, trailing semicolon(s)
    tokens = tokenize("x=3;")
    statements, rest = parse_statement_list(tokens)
    assert len(statements) == 1
    assert statements[0]["tag"] == "assign"
    assert rest[0]["tag"] is None

    tokens = tokenize("x=3;;;")
    statements, rest = parse_statement_list(tokens)
    assert len(statements) == 1
    assert statements[0]["tag"] == "assign"
    assert rest[0]["tag"] is None

    # leading semicolons
    tokens = tokenize(";;;x=3")
    statements, rest = parse_statement_list(tokens)
    assert len(statements) == 1
    assert statements[0]["tag"] == "assign"
    assert rest[0]["tag"] is None

    # two statements, single separator
    tokens = tokenize("x=3;print x")
    statements, rest = parse_statement_list(tokens)
    assert len(statements) == 2
    assert statements[0]["tag"] == "assign"
    assert statements[1]["tag"] == "print"
    assert rest[0]["tag"] is None

    # two statements, semicolon runs, plus trailing semicolons
    tokens = tokenize(";;;x=3;;;print x;;;")
    statements, rest = parse_statement_list(tokens)
    assert len(statements) == 2
    assert statements[0]["tag"] == "assign"
    assert statements[0]["target"] == "x"
    assert statements[1]["tag"] == "print"
    assert rest[0]["tag"] is None

    # missing semicolon between statements: statement_list stops and leaves rest
    tokens = tokenize("x=3print x")
    statements, rest = parse_statement_list(tokens)
    assert len(statements) == 1
    assert statements[0]["tag"] == "assign"
    assert rest[0]["tag"] == "print"

    # after a separator run, next token must start a statement
    try:
        tokens = tokenize("x=3;;;4")
        parse_statement_list(tokens)
    except SyntaxError:
        pass
    else:
        raise Exception("Expected SyntaxError: number cannot start a statement")

    # trailing separators are allowed
    tokens = tokenize("x=3;;;")
    statements, rest = parse_statement_list(tokens)
    assert len(statements) == 1
    assert rest[0]["tag"] is None

    # When '}' exists in the tokenizer, add:
    # tokens = tokenize("x=3; print x}")
    # statements, rest = parse_statement_list(tokens)
    # assert len(statements) == 2
    # assert rest[0]["tag"] == "}"


def parse(tokens):
    ast, tokens = parse_statement(tokens)
    if tokens[0]["tag"] is not None:
        raise SyntaxError(f"Unexpected token: {tokens[0]}")
    return ast


if __name__ == "__main__":
    test_parse_factor()
    test_parse_term()
    test_parse_expression()
    test_parse_print_statement()
    test_parse_assignment_statement()
    test_parse_statement()
    test_parse_statement_list()
    print("done.")
