# parser.py

from tokenizer import tokenize
from pprint import pprint

# EBNF

#   program = statement_list
#   statement_list = { ";" } [ statement { ";" { ";" } statement } ] { ";" }
#   print_statement = "print" expression
#   if_statement = "if" "(" expression ")" "{" statement_list "}" [ "else" "{" statement_list "}" ]
#   while_statement = "while" "(" expression ")" "{" statement_list "}"
#   assignment_statement = <identifier> "=" expression
#   function_statement = "function" identifier "(" [ identifier { "," identifier } ] ")" "{" statement_list "}"
#   statement = print_statement | if_statement | while_statement | function_statement | assignment_statement

#   expression = logic_or
#   logic_or   = logic_and { ("or" | "||")  logic_and }
#   logic_and  = logic_not { ("and" | "&&") logic_not }
#   logic_not  = [ ("not" | "!") ] comparison
#   comparison = arithmetic_expression [ compare_op arithmetic_expression ]
#   compare_op = "==" | "!=" | "<" | "<=" | ">" | ">="
#   arithmetic_expression = term { ("+" | "-") term }
#   term = unary { ("*" | "/") unary }
#   unary = { "-" } factor
#
#   ===== TOPIC-05 CHANGES: Added function expressions =====
#   factor = <number> | <identifier> | "(" expression ")" | "true" | "false" | function_expression
#   function_expression = "function" "(" [ identifier { "," identifier } ] ")" "{" statement_list "}"
#   ===== END TOPIC-05 CHANGES =====


def parse_factor(tokens):
    # factor = <number> | <identifier> | "(" expression ")" | "true" | "false" | function_expression
    token = tokens[0]
    if token["tag"] == "number":
        node = {"tag": "number", "value": token["value"]}
        return node, tokens[1:]
    if token["tag"] == "identifier":
        node = {"tag": "identifier", "value": token["value"]}
        return node, tokens[1:]
    if token["tag"] == "true":
        node = {"tag": "true"}
        return node, tokens[1:]
    if token["tag"] == "false":
        node = {"tag": "false"}
        return node, tokens[1:]
    # ===== TOPIC-05 CHANGES: Parse function expressions =====
    if token["tag"] == "function":
        return parse_function_expression(tokens)
    # ===== END TOPIC-05 CHANGES =====
    if token["tag"] == "(":
        node, tokens = parse_expression(tokens[1:])
        if tokens[0]["tag"] != ")":
            raise SyntaxError(f"Expected ')', got {tokens[0]}")
        return node, tokens[1:]
    raise SyntaxError(f"Expected factor, got {tokens[0]}")


# ===== TOPIC-05 CHANGES: Added complex expression parsing for function calls =====
def parse_complex_expression(tokens):
    # complex_expression = factor { "(" [ expression { "," expression } ] ")" }
    # This allows function calls like f() or f(1, 2, 3)
    ast, tokens = parse_factor(tokens)
    while tokens[0]["tag"] == "(":
        tokens = tokens[1:]
        arguments = []
        if tokens[0]["tag"] != ")":
            arg, tokens = parse_expression(tokens)
            arguments.append(arg)
            while tokens[0]["tag"] == ",":
                tokens = tokens[1:]
                arg, tokens = parse_expression(tokens)
                arguments.append(arg)
        if tokens[0]["tag"] != ")":
            raise SyntaxError(f"Expected ')' but got {tokens[0]}")
        tokens = tokens[1:]
        ast = {"tag": "call", "function": ast, "arguments": arguments}
    return ast, tokens


def test_parse_complex_expression():
    # complex_expression = factor { "(" [ expression { "," expression } ] ")" }
    print("test parse_complex_expression()")
    # Simple factor
    tokens = tokenize("3")
    ast, tokens = parse_complex_expression(tokens)
    assert ast == {"tag": "number", "value": 3}

    # Function call with no arguments
    tokens = tokenize("f()")
    ast, tokens = parse_complex_expression(tokens)
    assert ast["tag"] == "call"
    assert ast["function"]["tag"] == "identifier"
    assert ast["function"]["value"] == "f"
    assert ast["arguments"] == []

    # Function call with arguments
    tokens = tokenize("f(1, 2)")
    ast, tokens = parse_complex_expression(tokens)
    assert ast["tag"] == "call"
    assert len(ast["arguments"]) == 2


# ===== TOPIC-05 CHANGES: New function to parse function expressions =====
def parse_function_expression(tokens):
    # function_expression = "function" "(" [ identifier { "," identifier } ] ")" "{" statement_list "}"
    if tokens[0]["tag"] != "function":
        raise SyntaxError(f"Expected 'function', got {tokens[0]}")
    tokens = tokens[1:]

    if tokens[0]["tag"] != "(":
        raise SyntaxError(f"Expected '(', got {tokens[0]}")
    tokens = tokens[1:]

    parameters = []
    if tokens[0]["tag"] != ")":
        if tokens[0]["tag"] != "identifier":
            raise SyntaxError(f"Expected identifier, got {tokens[0]}")
        parameters.append(tokens[0]["value"])
        tokens = tokens[1:]
        while tokens[0]["tag"] == ",":
            tokens = tokens[1:]
            if tokens[0]["tag"] != "identifier":
                raise SyntaxError(f"Expected identifier, got {tokens[0]}")
            parameters.append(tokens[0]["value"])
            tokens = tokens[1:]

    if tokens[0]["tag"] != ")":
        raise SyntaxError(f"Expected ')', got {tokens[0]}")
    tokens = tokens[1:]

    if tokens[0]["tag"] != "{":
        raise SyntaxError(f"Expected '{{', got {tokens[0]}")
    tokens = tokens[1:]

    body, tokens = parse_statement_list(tokens)

    if tokens[0]["tag"] != "}":
        raise SyntaxError(f"Expected '}}', got {tokens[0]}")
    tokens = tokens[1:]

    return {
        "tag": "function",
        "parameters": parameters,
        "body": body,
    }, tokens


def parse_function_statement(tokens):
    # function_statement = "function" identifier "(" [ identifier { "," identifier } ] ")" "{" statement_list "}"
    assert tokens[0]["tag"] == "function", "Expected 'function'"
    tokens = tokens[1:]
    assert tokens[0]["tag"] == "identifier", "Expected function name"
    identifier_token = tokens[0]
    tokens = tokens[1:]
    # Rewrite the token stream into an assignment to a function expression.
    tokens = [
        identifier_token,
        {"tag": "=", "value": "="},
        {"tag": "function", "value": "function"},
    ] + tokens
    return parse_assignment_statement(tokens)

def test_parse_function_expression():
    print("test parse_function_expression()")
    tokens = tokenize("function(){}")
    ast, tokens = parse_unary(tokens)
    assert ast == {'tag': 'function', 'parameters': [], 'body': {'tag': 'statement_list', 'statements': []}}
    assert tokens[0]["tag"] == None

    tokens = tokenize("function(a,b){a=2;b=4}")
    ast, tokens = parse_unary(tokens)
    assert ast == {'tag': 'function', 'parameters': ['a', 'b'], 'body': {'tag': 'statement_list', 'statements': [{'tag': 'assign', 'target': 'a', 'expression': {'tag': 'number', 'value': 2}}, {'tag': 'assign', 'target': 'b', 'expression': {'tag': 'number', 'value': 4}}]}}
    assert tokens[0]["tag"] == None
    




# ===== END TOPIC-05 CHANGES =====


def test_parse_factor():
    """factor = <number> | <identifier> | "(" expression ")" | "true" | "false" | function_expression"""
    print("test parse_factor()")
    tokens = tokenize("3")
    ast, tokens = parse_factor(tokens)
    assert ast == {"tag": "number", "value": 3}
    assert tokens == [{"tag": None, "line": 1, "column": 2}]

    tokens = tokenize("true")
    ast, tokens = parse_factor(tokens)
    assert ast == {"tag": "true"}
    assert tokens == [{"tag": None, "line": 1, "column": 5}]

    tokens = tokenize("false")
    ast, tokens = parse_factor(tokens)
    assert ast == {"tag": "false"}
    assert tokens == [{"tag": None, "line": 1, "column": 6}]

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

    # ===== TOPIC-05 CHANGES: Added tests for function expressions =====
    # Test function expression with no parameters
    tokens = tokenize("function(){}")
    ast, tokens = parse_factor(tokens)
    assert ast["tag"] == "function"
    assert ast["parameters"] == []
    assert tokens[0]["tag"] == None

    # Test function expression with single parameter
    tokens = tokenize("function(x){print x;}")
    ast, tokens = parse_factor(tokens)
    assert ast["tag"] == "function"
    assert ast["parameters"] == ["x"]
    assert tokens[0]["tag"] == None

    # Test function expression with multiple parameters
    tokens = tokenize("function(x, y){}")
    ast, tokens = parse_factor(tokens)
    assert ast["tag"] == "function"
    assert ast["parameters"] == ["x", "y"]
    assert tokens[0]["tag"] == None


def test_parse_function_statement():
    print("test parse_function_statement()")
    tokens = tokenize("function f(x){y=1}")
    ast, tokens = parse_function_statement(tokens)
    assert ast == {
        "tag": "assign",
        "target": "f",
        "expression": {
            "tag": "function",
            "parameters": ["x"],
            "body": {
                "tag": "statement_list",
                "statements": [
                    {
                        "tag": "assign",
                        "target": "y",
                        "expression": {"tag": "number", "value": 1},
                    }
                ],
            },
        },
    }
    assert tokens[0]["tag"] == None
    # ===== END TOPIC-05 CHANGES =====


def parse_unary(tokens):
    # unary = { "-" } complex_expression
    minus_count = 0
    while tokens[0]["tag"] == "-":
        minus_count += 1
        tokens = tokens[1:]

    node, tokens = parse_complex_expression(tokens)

    # Apply unary minus operators from innermost to outermost
    for _ in range(minus_count):
        node = {"tag": "unary-", "operand": node}

    return node, tokens


def test_parse_unary():
    # unary = { "-" } factor
    print("test parse_unary()")
    tokens = tokenize("3")
    ast, tokens = parse_unary(tokens)
    assert ast == {"tag": "number", "value": 3}
    assert tokens == [{"tag": None, "line": 1, "column": 2}]

    tokens = tokenize("-3")
    ast, tokens = parse_unary(tokens)
    assert ast == {"tag": "unary-", "operand": {"tag": "number", "value": 3}}
    assert tokens == [{"tag": None, "line": 1, "column": 3}]

    tokens = tokenize("--3")
    ast, tokens = parse_unary(tokens)
    assert ast == {
        "tag": "unary-",
        "operand": {"tag": "unary-", "operand": {"tag": "number", "value": 3}},
    }
    assert tokens == [{"tag": None, "line": 1, "column": 4}]


def parse_term(tokens):
    # term = unary { ("*" | "/") unary }
    left, tokens = parse_unary(tokens)
    while tokens[0]["tag"] in ["*", "/"]:
        op = tokens[0]["tag"]
        right, tokens = parse_unary(tokens[1:])
        left = {"tag": op, "left": left, "right": right}
    return left, tokens


def test_parse_term():
    # term = unary { ("*" | "/") unary }
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


def parse_arithmetic_expression(tokens):
    # arithmetic_expression = term { ("+" | "-") term }
    left, tokens = parse_term(tokens)
    while tokens[0]["tag"] in ["+", "-"]:
        op = tokens[0]["tag"]
        right, tokens = parse_term(tokens[1:])
        left = {"tag": op, "left": left, "right": right}
    return left, tokens


def test_parse_arithmetic_expression():
    # arithmetic_expression = term { ("+" | "-") term }
    print("test parse_arithmetic_expression()")
    tokens = tokenize("3")
    ast, tokens = parse_arithmetic_expression(tokens)
    assert ast == {"tag": "number", "value": 3}
    assert tokens == [{"tag": None, "line": 1, "column": 2}]
    tokens = tokenize("3*4+5-6")
    ast, tokens = parse_arithmetic_expression(tokens)
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


def parse_comparison(tokens):
    # comparison = arithmetic_expression [ compare_op arithmetic_expression ]
    left, tokens = parse_arithmetic_expression(tokens)
    if tokens[0]["tag"] in ["==", "!=", "<", "<=", ">", ">="]:
        op = tokens[0]["tag"]
        right, tokens = parse_arithmetic_expression(tokens[1:])
        left = {"tag": op, "left": left, "right": right}
    return left, tokens


def test_parse_comparison():
    # comparison = arithmetic_expression [ compare_op arithmetic_expression ]
    print("test parse_comparison()")
    tokens = tokenize("3")
    ast, tokens = parse_comparison(tokens)
    assert ast == {"tag": "number", "value": 3}

    tokens = tokenize("3 == 4")
    ast, tokens = parse_comparison(tokens)
    assert ast == {
        "tag": "==",
        "left": {"tag": "number", "value": 3},
        "right": {"tag": "number", "value": 4},
    }

    tokens = tokenize("3 < 4")
    ast, tokens = parse_comparison(tokens)
    assert ast == {
        "tag": "<",
        "left": {"tag": "number", "value": 3},
        "right": {"tag": "number", "value": 4},
    }

    tokens = tokenize("3 >= 4")
    ast, tokens = parse_comparison(tokens)
    assert ast == {
        "tag": ">=",
        "left": {"tag": "number", "value": 3},
        "right": {"tag": "number", "value": 4},
    }


def parse_logic_not(tokens):
    # logic_not = [ "not" ] comparison
    if tokens[0]["tag"] == "not":
        tokens = tokens[1:]
        operand, tokens = parse_logic_not(tokens)
        return {"tag": "not", "operand": operand}, tokens
    else:
        return parse_comparison(tokens)


def test_parse_logic_not():
    # logic_not = [ "not" ] comparison
    print("test parse_logic_not()")
    tokens = tokenize("3")
    ast, tokens = parse_logic_not(tokens)
    assert ast == {"tag": "number", "value": 3}

    tokens = tokenize("not 3")
    ast, tokens = parse_logic_not(tokens)
    assert ast == {"tag": "not", "operand": {"tag": "number", "value": 3}}

    tokens = tokenize("not not 3")
    ast, tokens = parse_logic_not(tokens)
    assert ast == {
        "tag": "not",
        "operand": {"tag": "not", "operand": {"tag": "number", "value": 3}},
    }


def parse_logic_and(tokens):
    # logic_and = logic_not { "and" logic_not }
    left, tokens = parse_logic_not(tokens)
    while tokens[0]["tag"] == "and":
        right, tokens = parse_logic_not(tokens[1:])
        left = {"tag": "and", "left": left, "right": right}
    return left, tokens


def test_parse_logic_and():
    # logic_and = logic_not { "and" logic_not }
    print("test parse_logic_and()")
    tokens = tokenize("3")
    ast, tokens = parse_logic_and(tokens)
    assert ast == {"tag": "number", "value": 3}

    tokens = tokenize("3 and 4")
    ast, tokens = parse_logic_and(tokens)
    assert ast == {
        "tag": "and",
        "left": {"tag": "number", "value": 3},
        "right": {"tag": "number", "value": 4},
    }

    tokens = tokenize("3 and 4 and 5")
    ast, tokens = parse_logic_and(tokens)
    assert ast == {
        "tag": "and",
        "left": {
            "tag": "and",
            "left": {"tag": "number", "value": 3},
            "right": {"tag": "number", "value": 4},
        },
        "right": {"tag": "number", "value": 5},
    }


def parse_logic_or(tokens):
    # logic_or = logic_and { "or" logic_and }
    left, tokens = parse_logic_and(tokens)
    while tokens[0]["tag"] == "or":
        right, tokens = parse_logic_and(tokens[1:])
        left = {"tag": "or", "left": left, "right": right}
    return left, tokens


def test_parse_logic_or():
    # logic_or = logic_and { "or" logic_and }
    print("test parse_logic_or()")
    tokens = tokenize("3")
    ast, tokens = parse_logic_or(tokens)
    assert ast == {"tag": "number", "value": 3}

    tokens = tokenize("3 or 4")
    ast, tokens = parse_logic_or(tokens)
    assert ast == {
        "tag": "or",
        "left": {"tag": "number", "value": 3},
        "right": {"tag": "number", "value": 4},
    }

    tokens = tokenize("3 or 4 or 5")
    ast, tokens = parse_logic_or(tokens)
    assert ast == {
        "tag": "or",
        "left": {
            "tag": "or",
            "left": {"tag": "number", "value": 3},
            "right": {"tag": "number", "value": 4},
        },
        "right": {"tag": "number", "value": 5},
    }


def parse_expression(tokens):
    # expression = logic_or
    return parse_logic_or(tokens)


def test_parse_expression():
    # expression = logic_or
    print("test parse_expression()")
    tokens = tokenize("3")
    ast, tokens = parse_expression(tokens)
    assert ast == {"tag": "number", "value": 3}
    assert tokens == [{"tag": None, "line": 1, "column": 2}]
    tokens = tokenize("3 or 4 and 5")
    ast, tokens = parse_expression(tokens)
    assert ast == {
        "tag": "or",
        "left": {"tag": "number", "value": 3},
        "right": {
            "tag": "and",
            "left": {"tag": "number", "value": 4},
            "right": {"tag": "number", "value": 5},
        },
    }
    assert tokens[0]["tag"] is None


def parse_print_statement(tokens):
    # print_statement = "print" expression
    assert tokens[0]["tag"] == "print", "Expected 'print'"
    tokens = tokens[1:]
    ast, tokens = parse_expression(tokens)
    return {"tag": "print", "expression": ast}, tokens


def test_parse_print_statement():
    # print_statement = "print" expression
    print("test parse_print_statement()")
    tokens = tokenize("print 1")
    ast, tokens = parse_print_statement(tokens)
    assert ast == {"tag": "print", "expression": {"tag": "number", "value": 1}}
    assert tokens[0]["tag"] == None
    tokens = tokenize("print 1+1*3")
    ast, tokens = parse_print_statement(tokens)
    assert tokens[0]["tag"] == None


def parse_if_statement(tokens):
    # if_statement = "if" "(" expression ")" "{" statement_list "}" [ "else" "{" statement_list "}" ]
    assert tokens[0]["tag"] == "if", "Expected 'if'"
    tokens = tokens[1:]
    assert tokens[0]["tag"] == "(", "Expected '('"
    tokens = tokens[1:]
    condition, tokens = parse_expression(tokens)
    assert tokens[0]["tag"] == ")", "Expected ')'"
    tokens = tokens[1:]
    assert tokens[0]["tag"] == "{", "Expected '{'"
    tokens = tokens[1:]
    then_block, tokens = parse_statement_list(tokens)
    assert tokens[0]["tag"] == "}", "Expected '}'"
    tokens = tokens[1:]
    ast = {"tag": "if", "condition": condition, "then_block": then_block}
    if tokens[0]["tag"] == "else":
        tokens = tokens[1:]
        assert tokens[0]["tag"] == "{", "Expected '{'"
        tokens = tokens[1:]
        else_block, tokens = parse_statement_list(tokens)
        assert tokens[0]["tag"] == "}", "Expected '}'"
        tokens = tokens[1:]
        ast["else_block"] = else_block
    return ast, tokens


def test_parse_if_statement():
    # if_statement = "if" "(" expression ")" "{" statement_list "}" [ "else" "{" statement_list "}" ]
    print("test parse_if_statement()")
    tokens = tokenize("if(true){print 1}")
    ast, tokens = parse_if_statement(tokens)
    assert ast == {
        "tag": "if",
        "condition": {"tag": "true"},
        "then_block": {
            "tag": "statement_list",
            "statements": [
                {"tag": "print", "expression": {"tag": "number", "value": 1}}
            ],
        },
    }
    tokens = tokenize("if(true){print 1}else{print 2}")
    ast, tokens = parse_if_statement(tokens)
    assert ast == {
        "tag": "if",
        "condition": {"tag": "true"},
        "then_block": {
            "tag": "statement_list",
            "statements": [
                {"tag": "print", "expression": {"tag": "number", "value": 1}}
            ],
        },
        "else_block": {
            "tag": "statement_list",
            "statements": [
                {"tag": "print", "expression": {"tag": "number", "value": 2}}
            ],
        },
    }


def parse_while_statement(tokens):
    # while_statement = "while" "(" expression ")" "{" statement_list "}"
    assert tokens[0]["tag"] == "while", "Expected 'while'"
    tokens = tokens[1:]
    assert tokens[0]["tag"] == "(", "Expected '('"
    tokens = tokens[1:]
    condition, tokens = parse_expression(tokens)
    assert tokens[0]["tag"] == ")", "Expected ')'"
    tokens = tokens[1:]
    assert tokens[0]["tag"] == "{", "Expected '{'"
    tokens = tokens[1:]
    do_block, tokens = parse_statement_list(tokens)
    assert tokens[0]["tag"] == "}", "Expected '}'"
    tokens = tokens[1:]
    ast = {"tag": "while", "condition": condition, "do_block": do_block}
    return ast, tokens


def test_parse_while_statement():
    # while_statement = "while" "(" expression ")" "{" statement_list "}"
    tokens = tokenize("while(x>3){print x; x=x-1}")
    ast, tokens = parse_while_statement(tokens)
    assert ast == {
        "tag": "while",
        "condition": {
            "tag": ">",
            "left": {"tag": "identifier", "value": "x"},
            "right": {"tag": "number", "value": 3},
        },
        "do_block": {
            "tag": "statement_list",
            "statements": [
                {"tag": "print", "expression": {"tag": "identifier", "value": "x"}},
                {
                    "tag": "assign",
                    "target": "x",
                    "expression": {
                        "tag": "-",
                        "left": {"tag": "identifier", "value": "x"},
                        "right": {"tag": "number", "value": 1},
                    },
                },
            ],
        },
    }


def parse_assignment_statement(tokens):
    # assignment_statement = <identifier> "=" expression
    assert tokens[0]["tag"] == "identifier", "Expected <identifier>"
    identifier = tokens[0]["value"]
    tokens = tokens[1:]
    assert tokens[0]["tag"] == "=", "Expected '=' for assignment"
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
    # statement = print_statement | if_statement | while_statement | function_statement | assignment_statement
    if tokens[0]["tag"] == "print":
        return parse_print_statement(tokens)
    if tokens[0]["tag"] == "if":
        return parse_if_statement(tokens)
    if tokens[0]["tag"] == "while":
        return parse_while_statement(tokens)
    if tokens[0]["tag"] == "function":
        return parse_function_statement(tokens)
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
        return {"tag": "statement_list", "statements": statements}, tokens

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

    return {"tag": "statement_list", "statements": statements}, tokens


def test_parse_statement_list():
    print("test parse_statement_list()")

    # empty input
    tokens = tokenize("")
    ast, rest = parse_statement_list(tokens)
    assert ast["tag"] == "statement_list"
    assert ast["statements"] == []
    assert rest[0]["tag"] is None

    # only semicolons -> empty list
    tokens = tokenize(";;;")
    ast, rest = parse_statement_list(tokens)
    assert ast["tag"] == "statement_list"
    assert ast["statements"] == []
    assert rest[0]["tag"] is None

    # single statement, no semicolon
    tokens = tokenize("x=3")
    ast, rest = parse_statement_list(tokens)
    assert ast["tag"] == "statement_list"
    assert len(ast["statements"]) == 1
    assert ast["statements"][0]["tag"] == "assign"
    assert ast["statements"][0]["target"] == "x"
    assert rest[0]["tag"] is None

    # single statement, trailing semicolon(s)
    tokens = tokenize("x=3;")
    ast, rest = parse_statement_list(tokens)
    assert ast["tag"] == "statement_list"
    assert len(ast["statements"]) == 1
    assert ast["statements"][0]["tag"] == "assign"
    assert rest[0]["tag"] is None

    tokens = tokenize("x=3;;;")
    ast, rest = parse_statement_list(tokens)
    assert ast["tag"] == "statement_list"
    assert len(ast["statements"]) == 1
    assert ast["statements"][0]["tag"] == "assign"
    assert rest[0]["tag"] is None

    # leading semicolons
    tokens = tokenize(";;;x=3")
    ast, rest = parse_statement_list(tokens)
    assert ast["tag"] == "statement_list"
    assert len(ast["statements"]) == 1
    assert ast["statements"][0]["tag"] == "assign"
    assert rest[0]["tag"] is None

    # two statements, single separator
    tokens = tokenize("x=3;print x")
    ast, rest = parse_statement_list(tokens)
    assert ast["tag"] == "statement_list"
    assert len(ast["statements"]) == 2
    assert ast["statements"][0]["tag"] == "assign"
    assert ast["statements"][1]["tag"] == "print"
    assert rest[0]["tag"] is None

    # two statements, semicolon runs, plus trailing semicolons
    tokens = tokenize(";;;x=3;;;print x;;;")
    ast, rest = parse_statement_list(tokens)
    assert ast["tag"] == "statement_list"
    assert len(ast["statements"]) == 2
    assert ast["statements"][0]["tag"] == "assign"
    assert ast["statements"][0]["target"] == "x"
    assert ast["statements"][1]["tag"] == "print"
    assert rest[0]["tag"] is None

    # missing semicolon between statements: statement_list stops and leaves rest
    tokens = tokenize("x=3print x")
    ast, rest = parse_statement_list(tokens)
    assert ast["tag"] == "statement_list"
    assert len(ast["statements"]) == 1
    assert ast["statements"][0]["tag"] == "assign"
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
    ast, rest = parse_statement_list(tokens)
    assert ast["tag"] == "statement_list"
    assert len(ast["statements"]) == 1
    assert rest[0]["tag"] is None

    tokens = tokenize("x=3; print x}")
    ast, rest = parse_statement_list(tokens)
    assert ast["tag"] == "statement_list"
    assert len(ast["statements"]) == 2
    assert rest[0]["tag"] == "}"


def parse_program(tokens):
    ast, tokens = parse_statement_list(tokens)
    return {"tag": "program", "statements": ast}, tokens


def test_parse_program():
    print("test parse_program()")
    tokens = tokenize("x=3;print x")
    ast1, _ = parse_statement_list(tokens)
    ast2, _ = parse_program(tokens)
    assert ast2 == {"tag": "program", "statements": ast1}


def parse(tokens):
    ast, tokens = parse_program(tokens)
    if tokens[0]["tag"] is not None:
        raise SyntaxError(f"Unexpected token: {tokens[0]}")
    return ast


def test_parse():
    print("test parse()")
    tokens = tokenize("x=3;print x")
    ast, _ = parse_program(tokens)
    assert parse(tokens) == ast


if __name__ == "__main__":
    test_parse_factor()
    test_parse_unary()
    test_parse_term()
    test_parse_arithmetic_expression()
    test_parse_comparison()
    test_parse_logic_not()
    test_parse_logic_and()
    test_parse_logic_or()
    test_parse_expression()
    test_parse_print_statement()
    test_parse_if_statement()
    test_parse_while_statement()
    test_parse_assignment_statement()
    test_parse_statement()
    test_parse_statement_list()
    test_parse_program()
    test_parse_function_expression()
    test_parse_function_statement()
    test_parse()
    print("done.")
