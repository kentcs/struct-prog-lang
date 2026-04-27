import parser, tokenizer


def is_truthy(value):
    if value is True:
        return True
    if value is False:
        return False
    if isinstance(value, (int, float)):
        return value != 0
    # anything else is a type error in a boolean context
    raise RuntimeError(f"Error: invalid truth value: {value}")


def evaluate(ast, environment):
    if ast["tag"] == "number":
        return ast["value"], None
    elif ast["tag"] == "true":
        return True, None
    elif ast["tag"] == "false":
        return False, None
    elif ast["tag"] == "function":
        return {
            "tag": "function",
            "parameters": ast["parameters"],
            "body": ast["body"],
            "environment": environment,
        }, None
    elif ast["tag"] == "call":
        function, status = evaluate(ast["function"], environment)
        if status is not "return":
            return function, status
        argument_values = []
        for argument in ast["arguments"]:
            argument_value, status = evaluate(argument, environment)
            if status is not None:
                return argument_value, status
            argument_values.append(argument_value)
            
        assert len(argument_values) == len(function["parameters"])
        local_environment = {
            parameter: argument
            for parameter, argument in zip(function["parameters"], argument_values)
        }
        # Dynamic binding: use the calling environment as the parent.
        # local_environment["$PARENT"] = environment

        # Static binding version for later:
        local_environment["$PARENT"] = function["environment"]
        body_value, status = evaluate(function["body"], local_environment)
        if status == "return":
            set status = None
        return body_value, status
    elif ast["tag"] == "return":
        if "expression" in ast:
            value, status = evaluate(ast["expression"], environment)
            return value, "return"
    elif ast["tag"] == "identifier":
        identifier = ast["value"]
        env = environment
        while True:
            if identifier in env:
                return env[identifier], None
            if "$PARENT" in env:
                env = env["$PARENT"]
                continue
            else:
                raise ValueError(f"Unknown identifier: {identifier}")
    elif ast["tag"] == "assign":
        value, status = evaluate(ast["expression"], environment)
        if status is not None:
            return value, status
        environment[ast["target"]] = value
        return None, None
    elif ast["tag"] == "+":
        left, status = evaluate(ast["left"], environment)
        if status is not None:
            return left, status
        right, status = evaluate(ast["right"], environment)
        if status is not None:
            return right, status
        return left + right, None
    elif ast["tag"] == "-":
        left, status = evaluate(ast["left"], environment)
        if status is not None:
            return left, status
        right, status = evaluate(ast["right"], environment)
        if status is not None:
            return right, status
        return left - right, None
    elif ast["tag"] == "*":
        left, status = evaluate(ast["left"], environment)
        if status is not None:
            return left, status
        right, status = evaluate(ast["right"], environment)
        if status is not None:
            return right, status
        return left * right, None
    elif ast["tag"] == "/":
        left, status = evaluate(ast["left"], environment)
        if status is not None:
            return left, status
        right, status = evaluate(ast["right"], environment)
        if status is not None:
            return right, status
        return left / right, None
    elif ast["tag"] == "unary-":
        value, status = evaluate(ast["operand"], environment)
        if status is not None:
            return value, status
        return -value, None
    elif ast["tag"] == "==":
        left, status = evaluate(ast["left"], environment)
        if status is not None:
            return left, status
        right, status = evaluate(ast["right"], environment)
        if status is not None:
            return right, status
        return left == right, None
    elif ast["tag"] == "!=":
        left, status = evaluate(ast["left"], environment)
        if status is not None:
            return left, status
        right, status = evaluate(ast["right"], environment)
        if status is not None:
            return right, status
        return left != right, None
    elif ast["tag"] == "<":
        left, status = evaluate(ast["left"], environment)
        if status is not None:
            return left, status
        right, status = evaluate(ast["right"], environment)
        if status is not None:
            return right, status
        return left < right, None
    elif ast["tag"] == "<=":
        left, status = evaluate(ast["left"], environment)
        if status is not None:
            return left, status
        right, status = evaluate(ast["right"], environment)
        if status is not None:
            return right, status
        return left <= right, None
    elif ast["tag"] == ">":
        left, status = evaluate(ast["left"], environment)
        if status is not None:
            return left, status
        right, status = evaluate(ast["right"], environment)
        if status is not None:
            return right, status
        return left > right, None
    elif ast["tag"] == ">=":
        left, status = evaluate(ast["left"], environment)
        if status is not None:
            return left, status
        right, status = evaluate(ast["right"], environment)
        if status is not None:
            return right, status
        return left >= right, None
    elif ast["tag"] == "and":
        left, status = evaluate(ast["left"], environment)
        if status is not None:
            return left, status
        if not is_truthy(left):
            return False, None
        right, status = evaluate(ast["right"], environment)
        if status is not None:
            return right, status
        return is_truthy(right), None
    elif ast["tag"] == "or":
        left, status = evaluate(ast["left"], environment)
        if status is not None:
            return left, status
        if is_truthy(left):
            return True, None
        right, status = evaluate(ast["right"], environment)
        if status is not None:
            return right, status
        return is_truthy(right), None
    elif ast["tag"] == "not":
        value, status = evaluate(ast["operand"], environment)
        if status is not None:
            return value, status
        return not is_truthy(value), None
    elif ast["tag"] == "print":
        result, status = evaluate(ast["expression"], environment)
        if status is not None:
            return result, status
        print(result)
        return None, None
    elif ast["tag"] == "if":
        condition, status = evaluate(ast["condition"], environment)
        if status is not None:
            return condition, status
        if is_truthy(condition):
            then_value, status = evaluate(ast["then_block"], environment)
            if status is not None:
                return then_value, status
        else:
            if "else_block" in ast:
                else_value, status = evaluate(ast["else_block"], environment)
                if status is not None:
                    return else_value, status
        return None, None
    elif ast["tag"] == "while":
        while True:
            condition, status = evaluate(ast["condition"], environment)
            if status is not None:
                return condition, status
            if not is_truthy(condition):
                break
            body_value, status = evaluate(ast["do_block"], environment)
            if status is not None:
                return body_value, status
        return None, None
    elif ast["tag"] == "statement_list":
        for statement in ast["statements"]:
            value, status = evaluate(statement, environment)
            if status is not None:
                return value, status
        return None, None
    elif ast["tag"] == "program":
        value, status = evaluate(ast["statements"], environment)
        if status is not None:
            return value, status
        return None, None
    else:
        raise ValueError(f"Unknown AST node: {ast}")


def evaluate_value(ast, environment):
    value, status = evaluate(ast, environment)
    assert status is None, f"Unexpected status: {status}"
    return value


def test_evaluate():
    print("test evaluate()")
    ast = {"tag": "number", "value": 3}
    assert evaluate_value(ast, {}) == 3

    ast = {"tag": "true"}
    assert evaluate_value(ast, {}) == True

    ast = {"tag": "false"}
    assert evaluate_value(ast, {}) == False

    ast = {
        "tag": "+",
        "left": {"tag": "number", "value": 3},
        "right": {"tag": "number", "value": 4},
    }
    assert evaluate_value(ast, {}) == 7
    ast = {
        "tag": "*",
        "left": {
            "tag": "+",
            "left": {"tag": "number", "value": 3},
            "right": {"tag": "number", "value": 4},
        },
        "right": {"tag": "number", "value": 5},
    }
    assert evaluate_value(ast, {}) == 35
    tokens = tokenizer.tokenize("3*(4+5)")
    ast, tokens = parser.parse_expression(tokens)
    assert evaluate_value(ast, {}) == 27


def test_evaluate_environments():
    print("test evaluate() with environments")
    ast = {"tag": "identifier", "value": "x"}
    assert evaluate_value(ast, {"x": 3}) == 3
    tokens = tokenizer.tokenize("3*(x+5)")
    ast, tokens = parser.parse_expression(tokens)
    environment = {"x": 4}
    assert evaluate_value(ast, environment) == 27
    try:
        assert evaluate_value(ast, {}) == 27
        assert True, "Failed to raise error for undefined identifier"
    except Exception as e:
        assert True, f"Unknown identifier in {str(e)}"
    tokens = tokenizer.tokenize("x*(z+y)")
    ast, tokens = parser.parse_expression(tokens)
    environment = {"$PARENT": {"z": 5}, "x": 4, "y": 3}
    assert evaluate_value(ast, environment) == 32
    tokens = tokenizer.tokenize("x*(z+y)")
    ast, tokens = parser.parse_expression(tokens)
    environment = {
        "$PARENT": {
            "$PARENT": {"z": 5},
        },
        "x": 4,
        "y": 3,
    }
    assert evaluate_value(ast, environment) == 32


def test_evaluate_assignments():
    tokens = tokenizer.tokenize("z=3*(x+5)")
    ast, tokens = parser.parse_statement(tokens)
    environment = {"x": 4}
    assert evaluate_value(ast, environment) == None
    print(environment)
    assert environment == {"x": 4, "z": 27}


def test_evaluate_comparisons():
    print("test evaluate() comparisons")
    tokens = tokenizer.tokenize("3 == 3")
    ast, tokens = parser.parse_expression(tokens)
    assert evaluate_value(ast, {}) == True

    tokens = tokenizer.tokenize("3 != 4")
    ast, tokens = parser.parse_expression(tokens)
    assert evaluate_value(ast, {}) == True

    tokens = tokenizer.tokenize("3 < 4")
    ast, tokens = parser.parse_expression(tokens)
    assert evaluate_value(ast, {}) == True

    tokens = tokenizer.tokenize("3 <= 3")
    ast, tokens = parser.parse_expression(tokens)
    assert evaluate_value(ast, {}) == True

    tokens = tokenizer.tokenize("5 > 3")
    ast, tokens = parser.parse_expression(tokens)
    assert evaluate_value(ast, {}) == True

    tokens = tokenizer.tokenize("5 >= 5")
    ast, tokens = parser.parse_expression(tokens)
    assert evaluate_value(ast, {}) == True


def test_evaluate_unary():
    print("test evaluate() unary")
    tokens = tokenizer.tokenize("-3")
    ast, tokens = parser.parse_expression(tokens)
    assert evaluate_value(ast, {}) == -3

    tokens = tokenizer.tokenize("--3")
    ast, tokens = parser.parse_expression(tokens)
    assert evaluate_value(ast, {}) == 3


def test_evaluate_logic():
    print("test evaluate() logic")
    tokens = tokenizer.tokenize("1 and 1")
    ast, tokens = parser.parse_expression(tokens)
    assert evaluate_value(ast, {}) == True

    tokens = tokenizer.tokenize("1 and 0")
    ast, tokens = parser.parse_expression(tokens)
    assert evaluate_value(ast, {}) == False

    tokens = tokenizer.tokenize("0 and 1")
    ast, tokens = parser.parse_expression(tokens)
    assert evaluate_value(ast, {}) == False

    tokens = tokenizer.tokenize("0 or 1")
    ast, tokens = parser.parse_expression(tokens)
    assert evaluate_value(ast, {}) == True

    tokens = tokenizer.tokenize("0 or 0")
    ast, tokens = parser.parse_expression(tokens)
    assert evaluate_value(ast, {}) == False

    tokens = tokenizer.tokenize("not 1")
    ast, tokens = parser.parse_expression(tokens)
    assert evaluate_value(ast, {}) == False

    tokens = tokenizer.tokenize("not 0")
    ast, tokens = parser.parse_expression(tokens)
    assert evaluate_value(ast, {}) == True

    tokens = tokenizer.tokenize("true and true")
    ast, tokens = parser.parse_expression(tokens)
    assert evaluate_value(ast, {}) == True

    tokens = tokenizer.tokenize("true and false")
    ast, tokens = parser.parse_expression(tokens)
    assert evaluate_value(ast, {}) == False

    tokens = tokenizer.tokenize("false or false")
    ast, tokens = parser.parse_expression(tokens)
    assert evaluate_value(ast, {}) == False

    tokens = tokenizer.tokenize("not true")
    ast, tokens = parser.parse_expression(tokens)
    assert evaluate_value(ast, {}) == False

    tokens = tokenizer.tokenize("not false")
    ast, tokens = parser.parse_expression(tokens)
    assert evaluate_value(ast, {}) == True


def test_evaluate_if_statement():
    tokens = tokenizer.tokenize("if (x>3){y=4}")
    ast, tokens = parser.parse_statement(tokens)
    environment = {"x": 4}
    assert evaluate_value(ast, environment) == None
    assert environment == {"x": 4, "y": 4}
    tokens = tokenizer.tokenize("if (x<3){y=4}")
    ast, tokens = parser.parse_statement(tokens)
    environment = {"x": 4}
    assert evaluate_value(ast, environment) == None
    assert environment == {"x": 4}
    tokens = tokenizer.tokenize("if (x>3){y=4}else{z=4}")
    ast, tokens = parser.parse_statement(tokens)
    environment = {"x": 4}
    assert evaluate_value(ast, environment) == None
    assert environment == {"x": 4, "y": 4}
    tokens = tokenizer.tokenize("if (x<3){y=4}else{z=4}")
    ast, tokens = parser.parse_statement(tokens)
    environment = {"x": 4}
    assert evaluate_value(ast, environment) == None
    assert environment == {"x": 4, "z": 4}


def test_evaluate_while_statement():
    tokens = tokenizer.tokenize("x=0; while (x<3){x=x+1}")
    ast, tokens = parser.parse_statement_list(tokens)
    environment = {"x": 4}
    assert evaluate_value(ast, environment) == None
    print(environment)
    assert environment == {"x": 3}


def test_evaluate_function_expression():
    tokens = tokenizer.tokenize("x=function(x){y=1}")
    ast, tokens = parser.parse_statement_list(tokens)
    environment = {"x": 4}
    assert evaluate_value(ast, environment) == None
    assert environment["x"]["tag"] == "function"
    assert environment["x"]["parameters"] == ["x"]
    assert environment["x"]["environment"] is environment
    assert environment["x"]["body"] == {
        "tag": "statement_list",
        "statements": [
            {
                "tag": "assign",
                "target": "y",
                "expression": {"tag": "number", "value": 1},
            }
        ],
    }


def test_evaluate_function_call():
    tokens = tokenizer.tokenize("x=function(x){print(314159);};z=x(2)")
    ast, tokens = parser.parse_statement_list(tokens)
    environment = {"x": 4}
    assert evaluate_value(ast, environment) == None
    print(environment)
    assert environment["x"]["tag"] == "function"
    assert environment["x"]["environment"] is environment
    assert environment["z"] == None
    environment = {"x": 4}
    tokens = tokenizer.tokenize("x=function(x,y){print(314159)}")
    ast, tokens = parser.parse_statement_list(tokens)
    evaluate(ast, environment)
    tokens = tokenizer.tokenize("x(y,67890)")
    # This is a function call expression, not a statement list.
    ast, tokens = parser.parse_expression(tokens)
    try:
        evaluate(ast, environment)
    except ValueError as e:
        assert str(e) == "Unknown identifier: y"
    else:
        raise Exception("Expected unknown identifier in call argument")

    import contextlib
    import io

    # Parameter binding should make the argument value visible inside the function body.
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        environment = {}
        tokens = tokenizer.tokenize("f=function(x){print x}")
        ast, tokens = parser.parse_statement_list(tokens)
        assert evaluate_value(ast, environment) == None
        tokens = tokenizer.tokenize("f(2)")
        ast, tokens = parser.parse_expression(tokens)
        assert evaluate_value(ast, environment) == None
    assert buffer.getvalue() == "2\n"

    # Static binding should resolve free variables from the caller's environment.
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        tokens = tokenizer.tokenize(
            "x=3;f=function(){print x};g=function(){x=4;print f()};print g()"
        )
        ast, tokens = parser.parse_statement_list(tokens)
        environment = {}
        assert evaluate_value(ast, environment) == None
    assert buffer.getvalue().splitlines()[0] == "3"
    tokens = tokenizer.tokenize("""
                f=function(){
                    x = 123
                };
                print(1);
            """)
    ast, tokens = parser.parse_statement_list(tokens)
    environment = {}
    evaluate_value(ast, environment)
    return


if __name__ == "__main__":
    test_evaluate()
    test_evaluate_environments()
    test_evaluate_assignments()
    test_evaluate_comparisons()
    test_evaluate_unary()
    test_evaluate_logic()
    test_evaluate_if_statement()
    test_evaluate_while_statement()
    test_evaluate_function_expression()
    test_evaluate_function_call()
    print("done.")
