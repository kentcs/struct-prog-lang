from tokenizer import tokenize
from pprint import pprint

grammar = """
    simple_expression = identifier | <boolean> | <number> | <string> | <null> | list | object | ("-" simple_expression) | ("!" simple_expression) | function | ( "(" expression ")" )

    list = "[" expression { "," expression } "]"
    object = "{" [ expression ":" expression { "," expression ":" expression } ] "}"
    function = "function" "(" [ identifier { "," identifier } ] ")" statements

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




def parse_list(tokens):
    """
    list = "[" expression { "," expression } "]"
    """
    # A list literal starts with "[" and ends with "]".
    # Between them we allow zero or more expressions separated by commas.
    # Nested lists work because each item is parsed through parse_expression().
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




def parse_complex_expression(tokens):
    """
    complex_expression = simple_expression { ( ) | ("." identifier) | "(" [ expression { "," expression } ] ")" }
    """
    ast, tokens = parse_simple_expression(tokens)
    while tokens[0]["tag"] in ["[", ".", "("]:
        # The "[" branch is the list indexing case.
        # It lets us parse expressions like:
        #   x[0]
        #   x[1][2]
        #   nested[0][1]
        if tokens[0]["tag"] == "[":
            tokens = tokens[1:]
            index_ast, tokens = parse_expression(tokens)
            assert (
                tokens[0]["tag"] == "]"
            ), f"Expected ']' at position {tokens[0]['position']}"
            tokens = tokens[1:]
            ast = {"tag": "complex", "base": ast, "index": index_ast}
        if tokens[0]["tag"] == ".":
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




def parse_arithmetic_factor(tokens):
    """
    arithmetic_factor = complex_expression
    """
    return parse_complex_expression(tokens)




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




def parse_logical_factor(tokens):
    """
    logical_factor = relational_expression
    """
    return parse_relational_expression(tokens)




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




def parse_expression(tokens):
    """
    expression = assignment_expression
    """
    return parse_assignment_expression(tokens)




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




def parse_import_statement(tokens):
    """
    import_statement = "import" expression
    """
    assert tokens[0]["tag"] == "import"
    tokens = tokens[1:]
    value, tokens = parse_expression(tokens)
    return {"tag": "import", "value": value}, tokens




def parse_break_statement(tokens):
    """
    break_statement = "break"
    """
    assert tokens[0]["tag"] == "break"
    tokens = tokens[1:]
    return {"tag": "break"}, tokens




def parse_continue_statement(tokens):
    """
    continue_statement = "continue"
    """
    assert tokens[0]["tag"] == "continue"
    tokens = tokens[1:]
    return {"tag": "continue"}, tokens




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




def parse_program(tokens):
    """
    program = [ statement { ";" statement } ]
    """
    tokens = [{"tag": "{"}] + tokens[:-1] + [{"tag": "}"}] + tokens[-1:]
    ast, tokens = parse_statement_list(tokens)
    ast["tag"] = "program"
    return ast, tokens




def parse(tokens):
    ast, tokens = parse_program(tokens)
    return ast

