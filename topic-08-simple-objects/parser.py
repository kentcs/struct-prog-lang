from tokenizer import tokenize
from pprint import pprint

grammar = """
    simple_expression = identifier | <boolean> | <number> | <string> | <null> | list | object | ("-" simple_expression) | ("!" simple_expression) | function | ( "(" expression ")" )

    list = "[" expression { "," expression } "]"
    # Objects are dictionary-like values with explicit key:value pairs.
    object = "{" [ expression ":" expression { "," expression ":" expression } ] "}"
    function = "function" "(" [ identifier { "," identifier } ] ")" statements

    # Dot access is syntactic sugar for indexing with a string key.
    complex_expression = simple_expression { ("[" expression "]") | ("." identifier) | "(" [ expression { "," expression } ] ")" }

    arithmetic_factor = complex_expression
    arithmetic_term = arithmetic_factor { ("*" | "/") arithmetic_factor }
    arithmetic_expression = arithmetic_term { ("+" | "-") arithmetic_term }
    relational_expression = arithmetic_expression { ("<" | ">" | "<=" | ">=" | "==" | "!=") arithmetic_expression }
    logical_factor = relational_expression
    logical_term = logical_factor { "&&" logical_factor }
    logical_expression = logical_term { "||" logical_term }

    assignment_expression = [ "extern" ] logical_expression [ "=" assignment_expression ]
    expression = assignment_expression

    return_statement = "return" [ expression ]
    print_statement = "print" [ expression ]
    function_statement = "function" identifier "(" [ identifier { "," identifier } ] ")" statements

    if_statement = "if" "(" expression ")" statement_list [ "else" (if_statement | statement_list) ]
    while_statement = "while" "(" expression ")" statement_list
    statement_list = "{" statement { ";" statement } "}"
    exit_statement = "exit" [ expression ]
    assert_statement = "assert" expression [ "," expression ]
    import_statement = "import" expression
    break_statement = "break"
    continue_statement = "continue"

    statement = if_statement | while_statement | function_statement | return_statement | print_statement | exit_statement | import_statement | break_statement | continue_statement | assert_statement | expression

    program = [ statement { ";" statement } {";"} ]
    """


# BASIC EXPRESSIONS


def parse_simple_expression(tokens):
    """
    simple_expression = identifier | <boolean> | <number> | <string> | <null> | list | object | ("-" simple_expression) | ("!" simple_expression) | function | ( "(" expression ")" )
    """

    token = tokens[0]

    if token["tag"] in {"identifier", "boolean", "number", "string"}:
        return {"tag": token["tag"], "value": token["value"]}, tokens[1:]

    if token["tag"] == "null":
        return {"tag": "null"}, tokens[1:]

    if token["tag"] == "[":
        return parse_list(tokens)

    if token["tag"] == "{":
        return parse_object(tokens)

    if token["tag"] == "-":
        value, tokens = parse_simple_expression(tokens[1:])
        return {"tag": "negate", "value": value}, tokens

    if token["tag"] == "!":
        value, tokens = parse_simple_expression(tokens[1:])
        return {"tag": "not", "value": value}, tokens

    if token["tag"] == "function":
        return parse_function(tokens)

    if token["tag"] == "(":
        ast, tokens = parse_expression(tokens[1:])
        assert (
            tokens[0]["tag"] == ")"
        ), f"Expected ')' at position {tokens[0]['position']}"
        return ast, tokens[1:]

    assert False, f"Unexpected token '{token['tag']}' at position {token['position']}"


def test_parse_simple_expression():
    """
    simple_expression = identifier | <boolean> | <number> | <string> | <null> | list | object | ("-" simple_expression) | ("!" simple_expression) | function | ( "(" expression ")" )
    """
    print("testing parse_simple_expression...")

    node, remaining_tokens = parse_simple_expression(tokenize("x"))
    assert node["tag"] == "identifier"
    assert node["value"] == "x", f"Expected 'x', got {node['value']}"
    assert remaining_tokens[0]["tag"] is None, "Expected end of tokens"

    node, remaining_tokens = parse_simple_expression(tokenize("null"))
    assert node["tag"] == "null"
    assert remaining_tokens[0]["tag"] is None, "Expected end of tokens"

    for n in [1, 12, 1.3, 1.23]:
        node, remaining_tokens = parse_simple_expression(tokenize(str(n)))
        assert node["tag"] == "number"
        assert node["value"] == n, f"Expected {n}, got {result}"
        assert remaining_tokens[0]["tag"] is None, "Expected end of tokens"

    for s in ['""', '"hello"']:
        node, remaining_tokens = parse_simple_expression(tokenize(s))
        assert node["tag"] == "string"
        assert node["value"] == s.replace('"', ""), f"Expected {s}, got {result}"
        assert remaining_tokens[0]["tag"] is None, "Expected end of tokens"

    for s in ["[1,2,3]", "[]"]:
        t = tokenize(s)
        assert parse_simple_expression(t) == parse_list(t)

    for s in ['{"a":4,"b":"x"}', "{}"]:
        t = tokenize(s)
        assert parse_simple_expression(t) == parse_object(t)

    ast, tokens = parse_simple_expression(tokenize("-1"))
    assert ast == {"tag": "negate", "value": {"tag": "number", "value": 1}}

    ast, tokens = parse_simple_expression(tokenize("--2"))
    assert ast == {
        "tag": "negate",
        "value": {"tag": "negate", "value": {"tag": "number", "value": 2}},
    }

    ast, tokens = parse_simple_expression(tokenize("!1"))
    assert ast == {"tag": "not", "value": {"tag": "number", "value": 1}}

    ast, tokens = parse_simple_expression(tokenize("!!2"))
    assert ast == {
        "tag": "not",
        "value": {"tag": "not", "value": {"tag": "number", "value": 2}},
    }

    ast, tokens = parse_simple_expression(tokenize("(1+2)"))
    assert ast == {
        "tag": "+",
        "left": {"tag": "number", "value": 1},
        "right": {"tag": "number", "value": 2},
    }

    ast, tokens = parse_simple_expression(tokenize("(1+(2*3))"))
    assert ast == {
        "tag": "+",
        "left": {"tag": "number", "value": 1},
        "right": {
            "tag": "*",
            "left": {"tag": "number", "value": 2},
            "right": {"tag": "number", "value": 3},
        },
    }


def parse_list(tokens):
    """
    list = "[" expression { "," expression } "]"
    """
    assert tokens[0]["tag"] == "[", f"Expected '[' at position {tokens[0]['position']}"
    tokens = tokens[1:]
    items = []
    if tokens[0]["tag"] != "]":
        value, tokens = parse_expression(tokens)
        items.append(value)
        while tokens[0]["tag"] == ",":
            tokens = tokens[1:]
            if tokens[0]["tag"] == "]":  # allow for extra ","
                break
            value, tokens = parse_expression(tokens)
            items.append(value)
    assert (
        tokens[0]["tag"] == "]"
    ), f"Expected ']' at position {tokens[0]['position']}, got {tokens[0:]}."
    return {"tag": "list", "items": items}, tokens[1:]


def test_parse_list():
    """
    list = "[" expression { "," expression } "]"
    """
    print("testing parse_list...")
    ast, tokens = parse_list(tokenize("[1,2,3]"))
    print(ast)

    print("done")
    exit(0)

    # assert ast == {
    #     "tag": "list",
    #     "items": [
    #         {"tag": "number", "value": 1},
    #         {"tag": "number", "value": 2},
    #         {"tag": "number", "value": 3},
    #     ],
    # }
    # ast, tokens = parse_list(tokenize("[1,2,3,]"))
    # assert ast == {
    #     "tag": "list",
    #     "items": [
    #         {"tag": "number", "value": 1},
    #         {"tag": "number", "value": 2},
    #         {"tag": "number", "value": 3},
    #     ],
    # }
    # ast, tokens = parse_list(tokenize("[1,2,3,[4,5]]"))
    # assert ast == {
    #     "tag": "list",
    #     "items": [
    #         {"tag": "number", "value": 1},
    #         {"tag": "number", "value": 2},
    #         {"tag": "number", "value": 3},
    #         {
    #             "tag": "list",
    #             "items": [{"tag": "number", "value": 4}, {"tag": "number", "value": 5}],
    #         },
    #     ],
    # }

    # ast, tokens = parse_list(tokenize("[]"))
    # assert ast == {"items": [], "tag": "list"}

    ast = parse(
        tokenize(
            """
        function double(x) { return x+x };
        y = [1,2,3,double(4)]
        """
        )
    )
    print(ast)
    print("-----")
    ast = clean(ast)
    print(ast)
    exit(0)
    assert ast == {
        "tag": "program",
        "statements": [
            {
                "tag": "assign",
                "target": {"tag": "identifier", "value": "double"},
                "value": {
                    "tag": "function",
                    "parameters": [
                        {
                            "tag": "identifier",
                            "value": "x",
                        }
                    ],
                    "body": {
                        "tag": "statement_list",
                        "statements": [
                            {
                                "tag": "return",
                                "value": {
                                    "tag": "+",
                                    "left": {"tag": "identifier", "value": "x"},
                                    "right": {"tag": "identifier", "value": "x"},
                                },
                            }
                        ],
                    },
                },
            },
            {
                "tag": "assign",
                "target": {"tag": "identifier", "value": "y"},
                "value": {
                    "tag": "list",
                    "items": [
                        {"tag": "number", "value": 1},
                        {"tag": "number", "value": 2},
                        {"tag": "number", "value": 3},
                        {
                            "tag": "call",
                            "function": {"tag": "identifier", "value": "double"},
                            "arguments": [{"tag": "number", "value": 4}],
                        },
                    ],
                },
            },
        ],
    }


def parse_object(tokens):
    """
    object = "{" [ expression ":" expression { "," expression ":" expression } ] "}"
    """
    assert tokens[0]["tag"] == "{", f"Expected '{{' at position {tokens[0]['position']}"
    tokens = tokens[1:]
    items = []
    if tokens[0]["tag"] != "}":
        key, tokens = parse_expression(tokens)
        assert (
            tokens[0]["tag"] == ":"
        ), f"Expected ':' at position {tokens[0]['position']}"
        tokens = tokens[1:]
        value, tokens = parse_expression(tokens)
        items.append({"key": key, "value": value})
        while tokens[0]["tag"] == ",":
            tokens = tokens[1:]
            if tokens[0]["tag"] == "}":  # allow for extra ","
                break
            key, tokens = parse_expression(tokens)
            assert (
                tokens[0]["tag"] == ":"
            ), f"Expected ':' at position {tokens[0]['position']}"
            tokens = tokens[1:]
            value, tokens = parse_expression(tokens)
            items.append({"key": key, "value": value})
    assert tokens[0]["tag"] == "}", f"Expected '}}' at position {tokens[0]['position']}"
    return {"tag": "object", "items": items}, tokens[1:]


def test_parse_object():
    """
    object = "{" [ expression ":" expression { "," expression ":" expression } ] "}"
    """
    print("testing parse_object...")
    ast, tokens = parse_object(tokenize('{"a":4,"b":"x"}'))
    assert ast == {
        "tag": "object",
        "items": [
            {
                "key": {"tag": "string", "value": "a"},
                "value": {"tag": "number", "value": 4},
            },
            {
                "key": {"tag": "string", "value": "b"},
                "value": {"tag": "string", "value": "x"},
            },
        ],
    }
    ast, tokens = parse_object(tokenize('{"a":4,"b":"x",}'))
    assert ast == {
        "tag": "object",
        "items": [
            {
                "key": {"tag": "string", "value": "a"},
                "value": {"tag": "number", "value": 4},
            },
            {
                "key": {"tag": "string", "value": "b"},
                "value": {"tag": "string", "value": "x"},
            },
        ],
    }
    ast, tokens = parse_object(tokenize('{"a":4,"b":{"c":"d"},"e":[3,4]}'))
    assert ast == {
        "tag": "object",
        "items": [
            {
                "key": {"tag": "string", "value": "a"},
                "value": {"tag": "number", "value": 4},
            },
            {
                "key": {"tag": "string", "value": "b"},
                "value": {
                    "tag": "object",
                    "items": [
                        {
                            "key": {"tag": "string", "value": "c"},
                            "value": {"tag": "string", "value": "d"},
                        }
                    ],
                },
            },
            {
                "key": {"tag": "string", "value": "e"},
                "value": {
                    "tag": "list",
                    "items": [
                        {"tag": "number", "value": 3},
                        {"tag": "number", "value": 4},
                    ],
                },
            },
        ],
    }

    ast, tokens = parse_object(tokenize("{}"))
    assert ast == {"tag": "object", "items": []}


def parse_function(tokens):
    """
    function = "function" "(" [ identifier { "," identifier } ] ")" statements
    """
    assert (
        tokens[0]["tag"] == "function"
    ), f"Expected 'function' at position {tokens[0]['position']}"
    tokens = tokens[1:]
    assert tokens[0]["tag"] == "(", f"Expected '(' at position {tokens[0]['position']}"
    tokens = tokens[1:]
    parameters = []
    if tokens[0]["tag"] != ")":
        assert (
            tokens[0]["tag"] == "identifier"
        ), f"Expected identifier at position {tokens[0]['position']}"
        parameters.append(tokens[0])
        tokens = tokens[1:]
        while tokens[0]["tag"] == ",":
            tokens = tokens[1:]
            assert (
                tokens[0]["tag"] == "identifier"
            ), f"Expected identifier at position {tokens[0]['position']}"
            parameters.append(tokens[0])
            tokens = tokens[1:]
    assert tokens[0]["tag"] == ")", f"Expected ']' at position {tokens[0]['position']}"
    tokens = tokens[1:]
    body_statements, tokens = parse_statement_list(tokens)
    return {
        "tag": "function",
        "parameters": parameters,
        "body": body_statements,
    }, tokens


def test_parse_function():
    """
    function = "function" "(" [ identifier { "," identifier } ] ")" statements
    """
    print("testing parse_function...")
    ast, tokens = parse_function(tokenize("function(x,y){}"))
    assert ast == {
        "tag": "function",
        "parameters": [
            {"tag": "identifier", "value": "x", "position": 9},
            {"tag": "identifier", "value": "y", "position": 11},
        ],
        "body": {"tag": "statement_list", "statements": []},
    }
    ast, tokens = parse_function(tokenize("function(x,y){return x+y}"))
    assert ast == {
        "tag": "function",
        "parameters": [
            {"tag": "identifier", "value": "x", "position": 9},
            {"tag": "identifier", "value": "y", "position": 11},
        ],
        "body": {
            "tag": "statement_list",
            "statements": [
                {
                    "tag": "return",
                    "value": {
                        "tag": "+",
                        "left": {"tag": "identifier", "value": "x"},
                        "right": {"tag": "identifier", "value": "y"},
                    },
                }
            ],
        },
    }
    code = """
        x = 3; 
        function g(q)
            {return 2};
        g(4)
        """
    ast = parse(tokenize(code))
    assert ast == {
        "tag": "program",
        "statements": [
            {
                "tag": "assign",
                "target": {"tag": "identifier", "value": "x"},
                "value": {"tag": "number", "value": 3},
            },
            {
                "tag": "assign",
                "target": {"tag": "identifier", "value": "g"},
                "value": {
                    "tag": "function",
                    "parameters": [{"tag": "identifier", "value": "q", "position": 36}],
                    "body": {
                        "tag": "statement_list",
                        "statements": [
                            {"tag": "return", "value": {"tag": "number", "value": 2}}
                        ],
                    },
                },
            },
            {
                "tag": "call",
                "function": {"tag": "identifier", "value": "g"},
                "arguments": [{"tag": "number", "value": 4}],
            },
        ],
    }


def parse_complex_expression(tokens):
    """
    complex_expression = simple_expression { ( ) | ("." identifier) | "(" [ expression { "," expression } ] ")" }
    """
    ast, tokens = parse_simple_expression(tokens)
    while tokens[0]["tag"] in ["[", ".", "("]:
        if tokens[0]["tag"] == "[":
            # Bracket indexing is used for list indexing and object lookup.
            tokens = tokens[1:]
            index_ast, tokens = parse_expression(tokens)
            assert (
                tokens[0]["tag"] == "]"
            ), f"Expected ']' at position {tokens[0]['position']}"
            tokens = tokens[1:]
            ast = {"tag": "complex", "base": ast, "index": index_ast}
        if tokens[0]["tag"] == ".":
            # x.a becomes x["a"] at parse time.
            tokens = tokens[1:]
            assert (
                tokens[0]["tag"] == "identifier"
            ), f"Expected identifier at position {tokens[0]['position']}"
            ast = {
                "tag": "complex",
                "base": ast,
                "index": {"tag": "string", "value": tokens[0]["value"]},
            }
            tokens = tokens[1:]
        if tokens[0]["tag"] == "(":
            tokens = tokens[1:]
            items = []
            if tokens[0]["tag"] != ")":
                value, tokens = parse_expression(tokens)
                items.append(value)
                while tokens[0]["tag"] == ",":
                    value, tokens = parse_simple_expression(tokens[1:])
                    items.append(value)
            assert (
                tokens[0]["tag"] == ")"
            ), f"Expected ')' at position {tokens[0]['position']}"
            tokens = tokens[1:]
            ast = {"tag": "call", "function": ast, "arguments": items}
    return ast, tokens


def test_parse_complex_expression():
    """
    complex_expression = simple_expression { ("[" expression "]") | ("." identifier) | "(" [ expression { "," expression } ] ")" }
    """
    print("testing parse_complex_expression...")
    for s in ["x", '{"a":4,"b":"x"}', "{}"]:
        t = tokenize(s)
        assert parse_complex_expression(t) == parse_simple_expression(t)
    ast, tokens = parse_complex_expression(tokenize("x[3]"))
    assert ast == {
        "tag": "complex",
        "base": {"tag": "identifier", "value": "x"},
        "index": {"tag": "number", "value": 3},
    }
    ast, tokens = parse_complex_expression(tokenize('x["x"]'))
    assert ast == {
        "tag": "complex",
        "base": {"tag": "identifier", "value": "x"},
        "index": {"tag": "string", "value": "x"},
    }
    ast, tokens = parse_complex_expression(tokenize('x["x"][3]'))
    assert ast == {
        "tag": "complex",
        "base": {
            "tag": "complex",
            "base": {"tag": "identifier", "value": "x"},
            "index": {"tag": "string", "value": "x"},
        },
        "index": {"tag": "number", "value": 3},
    }
    ast, tokens = parse_complex_expression(tokenize("x.abc"))
    assert ast == {
        "tag": "complex",
        "base": {"tag": "identifier", "value": "x"},
        "index": {"tag": "string", "value": "abc"},
    }
    ast, tokens = parse_complex_expression(tokenize("x()"))
    assert ast == {
        "tag": "call",
        "function": {"tag": "identifier", "value": "x"},
        "arguments": [],
    }
    assert tokens[0]["tag"] == None

    ast, tokens = parse_complex_expression(tokenize("x(1,2)"))
    assert ast == {
        "tag": "call",
        "function": {"tag": "identifier", "value": "x"},
        "arguments": [{"tag": "number", "value": 1}, {"tag": "number", "value": 2}],
    }


# ARITHMETIC EXPRESSIONS


def parse_arithmetic_factor(tokens):
    """
    arithmetic_factor = complex_expression
    """
    return parse_complex_expression(tokens)


def test_parse_arithmetic_factor():
    """
    arithmetic_factor = complex_expression
    """
    print("testing parse_arithmetic_factor...")
    for expression in ["1", "1.2", "true", "x", "-1"]:
        t = tokenize(expression)
        assert parse_arithmetic_factor(t)[0] == parse_complex_expression(t)[0]


def parse_arithmetic_term(tokens):
    """
    arithmetic_term = arithmetic_factor { ("*" | "/") arithmetic_factor }
    """
    node, tokens = parse_arithmetic_factor(tokens)
    while tokens[0]["tag"] in ["*", "/", "%"]:
        tag = tokens[0]["tag"]
        next_node, tokens = parse_arithmetic_factor(tokens[1:])
        node = {"tag": tag, "left": node, "right": next_node}
    return node, tokens


def test_parse_arithmetic_term():
    """
    arithmetic_term = arithmetic_factor { ("*" | "/") arithmetic_factor }
    """
    print("testing parse_arithmetic_term...")
    ast, tokens = parse_arithmetic_term(tokenize("x"))
    assert ast == {"tag": "identifier", "value": "x"}

    ast, tokens = parse_arithmetic_term(tokenize("x*y"))
    assert ast == {
        "tag": "*",
        "left": {"tag": "identifier", "value": "x"},
        "right": {"tag": "identifier", "value": "y"},
    }

    ast, tokens = parse_arithmetic_term(tokenize("x/y"))
    assert ast == {
        "tag": "/",
        "left": {"tag": "identifier", "value": "x"},
        "right": {"tag": "identifier", "value": "y"},
    }

    ast, tokens = parse_arithmetic_term(tokenize("x*y/z"))
    assert ast == {
        "tag": "/",
        "left": {
            "tag": "*",
            "left": {"tag": "identifier", "value": "x"},
            "right": {"tag": "identifier", "value": "y"},
        },
        "right": {"tag": "identifier", "value": "z"},
    }


def parse_arithmetic_expression(tokens):
    """
    arithmetic_expression = arithmetic_term { ("+" | "-") arithmetic_term }
    """
    node, tokens = parse_arithmetic_term(tokens)
    while tokens[0]["tag"] in ["+", "-"]:
        tag = tokens[0]["tag"]
        next_node, tokens = parse_arithmetic_term(tokens[1:])
        node = {"tag": tag, "left": node, "right": next_node}
    return node, tokens


def test_parse_arithmetic_expression():
    """
    arithmetic_expression = arithmetic_term { ("+" | "-") arithmetic_term }
    """
    print("testing parse_arithmetic_expression...")
    assert parse_arithmetic_expression(tokenize("x"))[0] == {
        "tag": "identifier",
        "value": "x",
    }
    assert parse_arithmetic_expression(tokenize("x*y"))[0] == {
        "tag": "*",
        "left": {"tag": "identifier", "value": "x"},
        "right": {"tag": "identifier", "value": "y"},
    }
    assert parse_arithmetic_expression(tokenize("x+y"))[0] == {
        "tag": "+",
        "left": {"tag": "identifier", "value": "x"},
        "right": {"tag": "identifier", "value": "y"},
    }
    assert parse_arithmetic_expression(tokenize("x-y"))[0] == {
        "tag": "-",
        "left": {"tag": "identifier", "value": "x"},
        "right": {"tag": "identifier", "value": "y"},
    }
    assert parse_arithmetic_expression(tokenize("x+y-z"))[0] == {
        "tag": "-",
        "left": {
            "tag": "+",
            "left": {"tag": "identifier", "value": "x"},
            "right": {"tag": "identifier", "value": "y"},
        },
        "right": {"tag": "identifier", "value": "z"},
    }
    ast = parse_arithmetic_expression(tokenize("x+y*z"))[0]
    assert ast == {
        "tag": "+",
        "left": {"tag": "identifier", "value": "x"},
        "right": {
            "tag": "*",
            "left": {"tag": "identifier", "value": "y"},
            "right": {"tag": "identifier", "value": "z"},
        },
    }
    ast = parse_arithmetic_expression(tokenize("(x+y)*z"))[0]
    assert ast == {
        "tag": "*",
        "left": {
            "tag": "+",
            "left": {"tag": "identifier", "value": "x"},
            "right": {"tag": "identifier", "value": "y"},
        },
        "right": {"tag": "identifier", "value": "z"},
    }


# RELATIONAL EXPRESSIONS


def parse_relational_expression(tokens):
    """
    relational_expression = arithmetic_expression { ("<" | ">" | "<=" | ">=" | "==" | "!=") arithmetic_expression }
    """
    node, tokens = parse_arithmetic_expression(tokens)
    while tokens[0]["tag"] in ["<", ">", "<=", ">=", "==", "!="]:
        tag = tokens[0]["tag"]
        next_node, tokens = parse_arithmetic_expression(tokens[1:])
        node = {"tag": tag, "left": node, "right": next_node}
    return node, tokens


def test_parse_relational_expression():
    """
    relational_expression = arithmetic_expression { ("<" | ">" | "<=" | ">=" | "==" | "!=") arithmetic_expression }
    """
    print("testing parse_relational_expression...")
    assert parse_relational_expression(tokenize("x"))[0] == {
        "tag": "identifier",
        "value": "x",
    }
    for tag in ["<", ">", "<=", ">=", "==", "!="]:
        assert parse_relational_expression(tokenize(f"x{tag}y"))[0] == {
            "tag": tag,
            "left": {"tag": "identifier", "value": "x"},
            "right": {"tag": "identifier", "value": "y"},
        }
    assert parse_relational_expression(tokenize("x<y>z"))[0] == {
        "tag": ">",
        "left": {
            "tag": "<",
            "left": {"tag": "identifier", "value": "x"},
            "right": {"tag": "identifier", "value": "y"},
        },
        "right": {"tag": "identifier", "value": "z"},
    }


# LOGICAL EXPRESSIONS


def parse_logical_factor(tokens):
    """
    logical_factor = relational_expression
    """
    return parse_relational_expression(tokens)


def test_parse_logical_factor():
    """
    logical_factor = relational_expression
    """
    print("testing parse_logical_factor...")
    assert parse_logical_factor(tokenize("x"))[0] == {"tag": "identifier", "value": "x"}
    assert parse_logical_factor(tokenize("!x"))[0] == {
        "tag": "not",
        "value": {"tag": "identifier", "value": "x"},
    }


def parse_logical_term(tokens):
    """
    logical_term = logical_factor { "&&" logical_factor }
    """
    node, tokens = parse_logical_factor(tokens)
    while tokens[0]["tag"] == "&&":
        tag = tokens[0]["tag"]
        next_node, tokens = parse_logical_factor(tokens[1:])
        node = {"tag": tag, "left": node, "right": next_node}
    return node, tokens


def test_parse_logical_term():
    """
    logical_term = logical_factor { "&&" logical_factor }
    """
    print("testing parse_logical_term...")
    assert parse_logical_term(tokenize("x"))[0] == {"tag": "identifier", "value": "x"}
    assert parse_logical_term(tokenize("x&&y"))[0] == {
        "tag": "&&",
        "left": {"tag": "identifier", "value": "x"},
        "right": {"tag": "identifier", "value": "y"},
    }
    assert parse_logical_term(tokenize("x&&y&&z"))[0] == {
        "tag": "&&",
        "left": {
            "tag": "&&",
            "left": {"tag": "identifier", "value": "x"},
            "right": {"tag": "identifier", "value": "y"},
        },
        "right": {"tag": "identifier", "value": "z"},
    }


def parse_logical_expression(tokens):
    """
    logical_expression = logical_term { "||" logical_term }
    """
    node, tokens = parse_logical_term(tokens)
    while tokens[0]["tag"] == "||":
        tag = tokens[0]["tag"]
        next_node, tokens = parse_logical_term(tokens[1:])
        node = {"tag": tag, "left": node, "right": next_node}
    return node, tokens


def test_parse_logical_expression():
    """
    logical_expression = logical_term { "||" logical_term }
    """
    print("testing parse_logical_expression...")

    assert parse_logical_expression(tokenize("x"))[0] == {
        "tag": "identifier",
        "value": "x",
    }
    assert parse_logical_expression(tokenize("x||y"))[0] == {
        "tag": "||",
        "left": {"tag": "identifier", "value": "x"},
        "right": {"tag": "identifier", "value": "y"},
    }
    assert parse_logical_expression(tokenize("x||y&&z"))[0] == {
        "tag": "||",
        "left": {"tag": "identifier", "value": "x"},
        "right": {
            "tag": "&&",
            "left": {"tag": "identifier", "value": "y"},
            "right": {"tag": "identifier", "value": "z"},
        },
    }


def parse_assignment_expression(tokens):
    """
    assignment_expression = [ "extern" ] logical_expression [ "=" assignment_expression ]
    """
    extern = False
    if tokens[0]["tag"] == "extern":
        extern = True
        tokens = tokens[1:]

    left, tokens = parse_logical_expression(tokens)

    if tokens[0]["tag"] == "=":
        tokens = tokens[1:]
        right, tokens = parse_assignment_expression(tokens)

        # extern is only valid for simple identifiers
        if extern:
            if left["tag"] != "identifier":
                raise SyntaxError("extern can only be used with simple identifiers")
            left["extern"] = True

        return {"tag": "assign", "target": left, "value": right}, tokens

    # if no assignment occurred, extern must not be present
    assert not extern, "Can't use extern without assignment."

    return left, tokens


def test_parse_assignment_expression():
    """
    assignment_expression = [ "extern" ] logical_expression [ "=" assignment_expression ]
    """
    print("testing parse_assignment_expression...")

    # Simple value
    ast, tokens = parse_assignment_expression(tokenize("x"))
    assert ast == {"tag": "identifier", "value": "x"}

    # Basic assignment
    ast, tokens = parse_assignment_expression(tokenize("x = 3"))
    assert ast == {
        "tag": "assign",
        "target": {"tag": "identifier", "value": "x"},
        "value": {"tag": "number", "value": 3},
    }

    # Nested assignment
    ast, tokens = parse_assignment_expression(tokenize("x = y = 4"))
    assert ast == {
        "tag": "assign",
        "target": {"tag": "identifier", "value": "x"},
        "value": {
            "tag": "assign",
            "target": {"tag": "identifier", "value": "y"},
            "value": {"tag": "number", "value": 4},
        },
    }

    # Assignment with expression on RHS
    ast, tokens = parse_assignment_expression(tokenize("x = y + 1"))
    assert ast == {
        "tag": "assign",
        "target": {"tag": "identifier", "value": "x"},
        "value": {
            "tag": "+",
            "left": {"tag": "identifier", "value": "y"},
            "right": {"tag": "number", "value": 1},
        },
    }

    # extern assignment (valid)
    ast, tokens = parse_assignment_expression(tokenize("extern x = y + 1"))
    assert ast == {
        "tag": "assign",
        "target": {"tag": "identifier", "value": "x", "extern": True},
        "value": {
            "tag": "+",
            "left": {"tag": "identifier", "value": "y"},
            "right": {"tag": "number", "value": 1},
        },
    }

    # extern without assignment (invalid)
    try:
        parse_assignment_expression(tokenize("extern x"))
        assert False, "Expected error for 'extern' without '='"
    except AssertionError as e:
        assert "Can't use extern without assignment." in str(e)
        pass  # success — expected failure
    except Exception as e:
        assert False, f"Unexpected exception type: {e}"

    # extern with non-identifier LHS (invalid)
    try:
        parse_assignment_expression(tokenize("extern x[0] = 5"))
        assert False, "Expected syntax error for 'extern x[0] = 5'"
    except SyntaxError:
        pass  # success — expected failure


def parse_expression(tokens):
    """
    expression = assignment_expression
    """
    return parse_assignment_expression(tokens)


def test_parse_expression():
    """
    expression = assignment_expression
    """
    print("testing parse_expression...")
    for s in ["1", "1+1", "1 && 1", "1 < 2"]:
        t = tokenize(s)
        assert parse_expression(t) == parse_assignment_expression(t)


# STATEMENTS


def parse_statement_list(tokens):
    """
    statement_list = "{" statement { ";" statement } "}"
    """
    assert tokens[0]["tag"] == "{", f"Expected '{{' at position {tokens[0]['position']}"
    tokens = tokens[1:]
    statements = []
    while True:
        # terminate at end of statement list
        if tokens[0]["tag"] == "}":
            tokens = tokens[1:]
            return {"tag": "statement_list", "statements": statements}, tokens
        # skip extra separators
        if tokens[0]["tag"] == ";":
            tokens = tokens[1:]
            continue
        # parse a statement and add it to the list
        statement, tokens = parse_statement(tokens)
        statements.append(statement)
        # we don't need a semicolon terminator after block-terminated statements
        if statement["tag"] in ["if", "while", "function"]:
            continue
        # we don't need a semicolon terminator after function assignments
        if statement["tag"] == "assign" and statement["value"]["tag"] == "function":
            continue
        # otherwise require a terminator
        assert tokens[0]["tag"] in [";", "}"], f"Statement terminator missing {tokens}."


def test_parse_statement_list():
    """
    statement_list = "{" statement { ";" statement } "}"
    """
    print("testing parse_statements...")
    ast, tokens = parse_statement_list(tokenize("{}"))
    assert ast == {"tag": "statement_list", "statements": []}
    ast, tokens = parse_statement_list(tokenize("{print 2;print 3}"))
    assert ast == {
        "tag": "statement_list",
        "statements": [
            {"tag": "print", "value": {"tag": "number", "value": 2}},
            {"tag": "print", "value": {"tag": "number", "value": 3}},
        ],
    }
    ast, tokens = parse_statement_list(tokenize("{print 2;print 3;}"))
    assert ast == {
        "tag": "statement_list",
        "statements": [
            {"tag": "print", "value": {"tag": "number", "value": 2}},
            {"tag": "print", "value": {"tag": "number", "value": 3}},
        ],
    }
    ast, tokens = parse_statement_list(tokenize("{print 2;if (x) {4} print 3;}"))
    assert ast == {
        "tag": "statement_list",
        "statements": [
            {"tag": "print", "value": {"tag": "number", "value": 2}},
            {
                "tag": "if",
                "condition": {"tag": "identifier", "value": "x"},
                "then": {
                    "tag": "statement_list",
                    "statements": [{"tag": "number", "value": 4}],
                },
            },
            {"tag": "print", "value": {"tag": "number", "value": 3}},
        ],
    }
    ast, tokens = parse_statement_list(tokenize("{print 2;if (x) {4} print 3}"))
    assert ast == {
        "tag": "statement_list",
        "statements": [
            {"tag": "print", "value": {"tag": "number", "value": 2}},
            {
                "tag": "if",
                "condition": {"tag": "identifier", "value": "x"},
                "then": {
                    "tag": "statement_list",
                    "statements": [{"tag": "number", "value": 4}],
                },
            },
            {"tag": "print", "value": {"tag": "number", "value": 3}},
        ],
    }
    ast, tokens = parse_statement_list(tokenize("{print 2;function z(x) {4} print 3;}"))
    assert ast == {
        "tag": "statement_list",
        "statements": [
            {"tag": "print", "value": {"tag": "number", "value": 2}},
            {
                "tag": "assign",
                "target": {"tag": "identifier", "value": "z"},
                "value": {
                    "tag": "function",
                    "parameters": [{"tag": "identifier", "value": "x", "position": 20}],
                    "body": {
                        "tag": "statement_list",
                        "statements": [{"tag": "number", "value": 4}],
                    },
                },
            },
            {"tag": "print", "value": {"tag": "number", "value": 3}},
        ],
    }
    ast, tokens = parse_statement_list(
        tokenize("{print 2;z = function (x) {4} print 3;}")
    )
    assert ast == {
        "tag": "statement_list",
        "statements": [
            {"tag": "print", "value": {"tag": "number", "value": 2}},
            {
                "tag": "assign",
                "target": {"tag": "identifier", "value": "z"},
                "value": {
                    "tag": "function",
                    "parameters": [{"tag": "identifier", "value": "x", "position": 23}],
                    "body": {
                        "tag": "statement_list",
                        "statements": [{"tag": "number", "value": 4}],
                    },
                },
            },
            {"tag": "print", "value": {"tag": "number", "value": 3}},
        ],
    }


def parse_if_statement(tokens):
    """
    if_statement = "if" "(" expression ")" statement_list [ "else" (if_statement | statement_list) ]
    """
    assert tokens[0]["tag"] == "if"
    tokens = tokens[1:]
    if tokens[0]["tag"] != "(":
        raise Exception(f"Expected '(': {tokens[0]}")
    condition, tokens = parse_expression(tokens[1:])
    if tokens[0]["tag"] != ")":
        raise Exception(f"Expected ')': {tokens[0]}")
    then_statements, tokens = parse_statement_list(tokens[1:])
    node = {
        "tag": "if",
        "condition": condition,
        "then": then_statements,
    }
    if tokens[0]["tag"] == "else":
        tokens = tokens[1:]
        assert tokens[0]["tag"] in [
            "{",
            "if",
        ], "Else must be followed by statements or if statement."
        if tokens[0]["tag"] == "{":
            else_statements, tokens = parse_statement_list(tokens)
        else:
            else_statements, tokens = parse_if_statement(tokens)
        node["else"] = else_statements
    return node, tokens


def test_parse_if_statement():
    """
    if_statement = "if" "(" expression ")" statement_list [ "else" (if_statement | statement_list) ]
    """
    print("testing parse_if_statement...")
    ast = parse_if_statement(tokenize("if(1){}"))[0]
    assert ast == {
        "tag": "if",
        "condition": {"tag": "number", "value": 1},
        "then": {"tag": "statement_list", "statements": []},
    }
    ast = parse_if_statement(tokenize("if(1){print 1}"))[0]
    assert ast == {
        "tag": "if",
        "condition": {"tag": "number", "value": 1},
        "then": {
            "tag": "statement_list",
            "statements": [{"tag": "print", "value": {"tag": "number", "value": 1}}],
        },
    }
    ast = parse_if_statement(tokenize("if(1){print 1}else{print 2}"))[0]
    assert ast == {
        "tag": "if",
        "condition": {"tag": "number", "value": 1},
        "then": {
            "tag": "statement_list",
            "statements": [{"tag": "print", "value": {"tag": "number", "value": 1}}],
        },
        "else": {
            "tag": "statement_list",
            "statements": [{"tag": "print", "value": {"tag": "number", "value": 2}}],
        },
    }


def parse_while_statement(tokens):
    """
    while_statement = "while" "(" expression ")" statement_list
    """
    assert tokens[0]["tag"] == "while"
    tokens = tokens[1:]
    if tokens[0]["tag"] != "(":
        raise Exception(f"Expected '(': {tokens[0]}")
    condition, tokens = parse_expression(tokens[1:])
    if tokens[0]["tag"] != ")":
        raise Exception(f"Expected ')': {tokens[0]}")
    do_statements, tokens = parse_statement_list(tokens[1:])
    return {"tag": "while", "condition": condition, "do": do_statements}, tokens


def test_parse_while_statement():
    """
    while_statement = "while" "(" expression ")" statement_list
    """
    print("testing parse_while_statement...")
    ast = parse_while_statement(tokenize("while(1){print 1}"))[0]
    assert ast == {
        "tag": "while",
        "condition": {"tag": "number", "value": 1},
        "do": {
            "tag": "statement_list",
            "statements": [{"tag": "print", "value": {"tag": "number", "value": 1}}],
        },
    }


def parse_return_statement(tokens):
    """
    return_statement = "return" [ expression ]
    """
    assert tokens[0]["tag"] == "return"
    tokens = tokens[1:]
    if tokens[0]["tag"] in ["}", ";", None]:
        value = None
        return {"tag": "return"}, tokens
    else:
        value, tokens = parse_expression(tokens)
        return {"tag": "return", "value": value}, tokens


def test_parse_return_statement():
    """
    return_statement = "return" [ expression ]
    """
    print("testing parse_return_statement...")
    ast = parse_return_statement(tokenize("return"))[0]
    assert ast == {"tag": "return"}
    ast = parse_return_statement(tokenize("return}12"))[0]
    assert ast == {"tag": "return"}
    ast = parse_return_statement(tokenize("return;34"))[0]
    assert ast == {"tag": "return"}
    ast = parse_return_statement(tokenize("return 5"))[0]
    assert ast == {"tag": "return", "value": {"tag": "number", "value": 5}}
    ast = parse_return_statement(tokenize("return (5)"))[0]
    assert ast == {"tag": "return", "value": {"tag": "number", "value": 5}}


def parse_print_statement(tokens):
    """
    print_statement = "print" [ expression ]
    """
    assert tokens[0]["tag"] == "print"
    tokens = tokens[1:]
    if tokens[0]["tag"] in ["}", ";", None]:
        # no expression
        return {"tag": "print", "value": None}, tokens
    else:
        value, tokens = parse_expression(tokens)
        return {"tag": "print", "value": value}, tokens


def test_parse_print_statement():
    """
    print_statement = "print" [ expression ]
    """
    print("testing parse_print_statement...")
    ast = parse_print_statement(tokenize("print 1"))[0]
    assert ast == {"tag": "print", "value": {"tag": "number", "value": 1}}


def parse_exit_statement(tokens):
    """
    exit_statement = "exit" [ expression ]
    """
    assert tokens[0]["tag"] == "exit"
    tokens = tokens[1:]
    if tokens[0]["tag"] in ["}", ";", None]:
        # no expression
        return {"tag": "exit", "value": None}, tokens
    else:
        value, tokens = parse_expression(tokens)
        return {"tag": "exit", "value": value}, tokens


def test_parse_exit_statement():
    """
    exit_statement = "exit" [ expression ]
    """
    print("testing parse_exit_statement...")
    ast = parse_exit_statement(tokenize("exit 1"))[0]
    assert ast == {"tag": "exit", "value": {"tag": "number", "value": 1}}


def parse_import_statement(tokens):
    """
    import_statement = "import" expression
    """
    assert tokens[0]["tag"] == "import"
    tokens = tokens[1:]
    value, tokens = parse_expression(tokens)
    return {"tag": "import", "value": value}, tokens


def test_parse_import_statement():
    """
    import_statement = "import" expression
    """
    print("testing parse_import_statement...")
    ast = parse_import_statement(tokenize('import "abc.t"'))[0]
    assert ast == {"tag": "import", "value": {"tag": "string", "value": "abc.t"}}


def parse_break_statement(tokens):
    """
    break_statement = "break"
    """
    assert tokens[0]["tag"] == "break"
    tokens = tokens[1:]
    return {"tag": "break"}, tokens


def test_parse_break_statement():
    """
    break_statement = "break"
    """
    print("testing parse_break_statement...")
    ast = parse_break_statement(tokenize("break"))[0]
    assert ast == {"tag": "break"}


def parse_continue_statement(tokens):
    """
    continue_statement = "continue"
    """
    assert tokens[0]["tag"] == "continue"
    tokens = tokens[1:]
    return {"tag": "continue"}, tokens


def test_parse_continue_statement():
    """
    continue_statement = "continue"
    """
    print("testing parse_continue_statement...")
    ast = parse_continue_statement(tokenize("continue"))[0]
    assert ast == {"tag": "continue"}


def parse_function_statement(tokens):
    """
    function_statement = "function" identifier "(" [ identifier { "," identifier } ] ")" statements
    """
    assert tokens[0]["tag"] == "function"
    tokens = tokens[1:]
    assert tokens[0]["tag"] == "identifier"
    identifier_token = tokens[0]
    tokens = tokens[1:]
    tokens = [
        identifier_token,
        {"tag": "=", "value": "="},
        {"tag": "function", "value": "function"},
    ] + tokens
    return parse_assignment_expression(tokens)


def parse_assert_statement(tokens):
    """
    assert_statement = "assert" expression [ "," expression ]
    """
    assert tokens[0]["tag"] == "assert"
    tokens = tokens[1:]
    condition, tokens = parse_expression(tokens)
    if tokens[0]["tag"] == ",":
        tokens = tokens[1:]
        explanation, tokens = parse_expression(tokens)
        return {
            "tag": "assert",
            "condition": condition,
            "explanation": explanation,
        }, tokens
    else:
        return {"tag": "assert", "condition": condition}, tokens


def test_parse_assert_statement():
    """
    assert_statement = "assert" expression [ "," expression ]
    """
    print("testing parse_assert_statement...")
    ast = parse_assert_statement(tokenize("assert 1"))[0]
    assert ast == {"tag": "assert", "condition": {"tag": "number", "value": 1}}
    ast = parse_assert_statement(tokenize("assert 1,2"))[0]
    assert ast == {
        "tag": "assert",
        "condition": {"tag": "number", "value": 1},
        "explanation": {"tag": "number", "value": 2},
    }


def test_parse_function_statement():
    """
    function_statement = "function" identifier "(" [ identifier { "," identifier } ] ")" statements
    """
    print("testing parse_function_statement...")
    ast, result = parse_function_statement(tokenize("function x(y){2}"))
    assert ast == {
        "tag": "assign",
        "target": {"tag": "identifier", "value": "x"},
        "value": {
            "body": {
                "tag": "statement_list",
                "statements": [{"tag": "number", "value": 2}],
            },
            "parameters": [{"position": 11, "tag": "identifier", "value": "y"}],
            "tag": "function",
        },
    }


def parse_statement(tokens):
    """
    statement = if_statement | while_statement | function_statement | return_statement | print_statement | exit_statement | import_statement | break_statement | continue_statement | assert_statement | expression
    """
    tag = tokens[0]["tag"]
    # note: none of these consumes a token
    if tag == "if":
        return parse_if_statement(tokens)
    if tag == "while":
        return parse_while_statement(tokens)
    if tag == "function":
        return parse_function_statement(tokens)
    if tag == "return":
        return parse_return_statement(tokens)
    if tag == "print":
        return parse_print_statement(tokens)
    if tag == "exit":
        return parse_exit_statement(tokens)
    if tag == "import":
        return parse_import_statement(tokens)
    if tag == "break":
        return parse_break_statement(tokens)
    if tag == "continue":
        return parse_continue_statement(tokens)
    if tag == "assert":
        return parse_assert_statement(tokens)
    return parse_expression(tokens)


def test_parse_statement():
    """
    statement = if_statement | while_statement | function_statement | return_statement | print_statement | exit_statement | import_statement | break_statement | continue_statement | assert_statement | expression
    """
    print("testing parse_statement...")

    # if statement
    assert (
        parse_statement(tokenize("if(1){print 1}"))[0]
        == parse_if_statement(tokenize("if(1){print 1}"))[0]
    )
    # # while statement
    assert (
        parse_statement(tokenize("while(1){print 1}"))[0]
        == parse_while_statement(tokenize("while(1){print 1}"))[0]
    )
    # return statement
    assert (
        parse_statement(tokenize("return 22"))[0]
        == parse_return_statement(tokenize("return 22"))[0]
    )
    # print statement
    assert (
        parse_statement(tokenize("print 1"))[0]
        == parse_print_statement(tokenize("print 1"))[0]
    )
    # function_statement (syntactic sugar)
    assert (
        parse_statement(tokenize("function x(y){2}"))[0]
        == parse_function_statement(tokenize("function x(y){2}"))[0]
    )


def parse_program(tokens):
    """
    program = [ statement { ";" statement } ]
    """
    tokens = [{"tag": "{"}] + tokens[:-1] + [{"tag": "}"}] + tokens[-1:]
    ast, tokens = parse_statement_list(tokens)
    ast["tag"] = "program"
    return ast, tokens


def test_parse_program():
    """
    program = [ statement { ";" statement } {";"} ]
    """
    print("testing parse_program...")
    ast, tokens = parse_program(tokenize("print 1; print 2"))
    assert ast == {
        "tag": "program",
        "statements": [
            {"tag": "print", "value": {"tag": "number", "value": 1}},
            {"tag": "print", "value": {"tag": "number", "value": 2}},
        ],
    }
    ast, tokens = parse_program(tokenize("print 1; print 2;"))
    assert ast == {
        "tag": "program",
        "statements": [
            {"tag": "print", "value": {"tag": "number", "value": 1}},
            {"tag": "print", "value": {"tag": "number", "value": 2}},
        ],
    }
    code = """if (1) {print 3} print 4; print 5"""
    ast, tokens = parse_program(tokenize(code))
    assert ast == {
        "tag": "program",
        "statements": [
            {
                "tag": "if",
                "condition": {"tag": "number", "value": 1},
                "then": {
                    "tag": "statement_list",
                    "statements": [
                        {"tag": "print", "value": {"tag": "number", "value": 3}}
                    ],
                },
            },
            {"tag": "print", "value": {"tag": "number", "value": 4}},
            {"tag": "print", "value": {"tag": "number", "value": 5}},
        ],
    }


def parse(tokens):
    ast, tokens = parse_program(tokens)
    return ast


def test_parse():
    print("testing parse")
    tokens = tokenize("2+3*4+5")
    ast = parse(tokens)
    assert ast == {
        "tag": "program",
        "statements": [
            {
                "left": {
                    "left": {"tag": "number", "value": 2},
                    "right": {
                        "left": {"tag": "number", "value": 3},
                        "right": {"tag": "number", "value": 4},
                        "tag": "*",
                    },
                    "tag": "+",
                },
                "right": {"tag": "number", "value": 5},
                "tag": "+",
            }
        ],
    }
    tokens = tokenize("1*2<3*4||5>6&&7")
    ast = parse(tokens)
    assert ast == {
        "tag": "program",
        "statements": [
            {
                "tag": "||",
                "left": {
                    "tag": "<",
                    "left": {
                        "tag": "*",
                        "left": {"tag": "number", "value": 1},
                        "right": {"tag": "number", "value": 2},
                    },
                    "right": {
                        "tag": "*",
                        "left": {"tag": "number", "value": 3},
                        "right": {"tag": "number", "value": 4},
                    },
                },
                "right": {
                    "tag": "&&",
                    "left": {
                        "tag": ">",
                        "left": {"tag": "number", "value": 5},
                        "right": {"tag": "number", "value": 6},
                    },
                    "right": {"tag": "number", "value": 7},
                },
            }
        ],
    }
    tokens = tokenize(
        """if(1){
                            function d(x) {return x + x}
                            print(d(4))
                         }
                      """
    )
    ast = parse(tokens)


if __name__ == "__main__":
    # List of all test functions
    old_test_functions = [
        test_parse_simple_expression,
        test_parse_list,
        test_parse_object,
        test_parse_function,
        test_parse_complex_expression,
        test_parse_arithmetic_factor,
        test_parse_arithmetic_term,
        test_parse_arithmetic_expression,
        test_parse_relational_expression,
        test_parse_logical_factor,
        test_parse_logical_term,
        test_parse_logical_expression,
        test_parse_assignment_expression,
        test_parse_expression,
        test_parse_statement_list,
        test_parse_if_statement,
        test_parse_while_statement,
        test_parse_return_statement,
        test_parse_print_statement,
        test_parse_function_statement,
        test_parse_exit_statement,
        test_parse_break_statement,
        test_parse_continue_statement,
        test_parse_import_statement,
        test_parse_assert_statement,
        test_parse_statement,
        test_parse_program,
    ]

    test_functions = [
        test_parse_simple_expression,
    ]
    test_grammar = grammar

    # Run each test function
    for test_function in test_functions:
        rule = test_function.__doc__.strip().replace("Tests  ", "")
        assert rule in grammar, f"rule [[[ {rule} ]]] not in grammar."
        test_grammar = test_grammar.replace(rule + "\n", "")
        test_function()

    if test_grammar.strip() != "":
        print(f"Untested grammar = [[[ {test_grammar} ]]]")

    test_parse()
