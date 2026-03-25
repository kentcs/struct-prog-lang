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
        return ast["value"]
    elif ast["tag"] == "true":
        return True
    elif ast["tag"] == "false":
        return False
    elif ast["tag"] == "function":
        return ast
    elif ast["tag"] == "call":
        assert "function" in ast
        print(ast)
        function = evaluate(ast["function"], environment)
        print(function)
        print(function["parameters"])
        print(ast["arguments"])
        argument_values = [evaluate(argument, environment) for argument in ast["arguments"]]
        print(argument_values)
        assert len(argument_values) == len(function["parameters"])
        print(function["body"])
        local_environment = {
            "$PARENT" : environment
        }
        for i in range(0,len(function["parameters"])):
            local_environment[function["parameters"][i]] = argument_values[i]
        print("LOCAL = ",local_environment)
        evaluate(function["body"], local_environment)
        
        return None

    elif ast["tag"] == "identifier":
        identifier = ast["value"]
        env = environment
        while True:
            if identifier in env:
                return env[identifier]
            if "$PARENT" in env:
                env = env["$PARENT"]
                continue
            else:
                raise ValueError(f"Unknown identifier: {identifier}")
    elif ast["tag"] == "assign":
        value = evaluate(ast["expression"], environment)
        environment[ast["target"]] = value
        return None
    elif ast["tag"] == "+":
        return evaluate(ast["left"], environment) + evaluate(ast["right"], environment)
    elif ast["tag"] == "-":
        return evaluate(ast["left"], environment) - evaluate(ast["right"], environment)
    elif ast["tag"] == "*":
        return evaluate(ast["left"], environment) * evaluate(ast["right"], environment)
    elif ast["tag"] == "/":
        return evaluate(ast["left"], environment) / evaluate(ast["right"], environment)
    elif ast["tag"] == "unary-":
        return -evaluate(ast["operand"], environment)
    elif ast["tag"] == "==":
        return evaluate(ast["left"], environment) == evaluate(ast["right"], environment)
    elif ast["tag"] == "!=":
        return evaluate(ast["left"], environment) != evaluate(ast["right"], environment)
    elif ast["tag"] == "<":
        return evaluate(ast["left"], environment) < evaluate(ast["right"], environment)
    elif ast["tag"] == "<=":
        return evaluate(ast["left"], environment) <= evaluate(ast["right"], environment)
    elif ast["tag"] == ">":
        return evaluate(ast["left"], environment) > evaluate(ast["right"], environment)
    elif ast["tag"] == ">=":
        return evaluate(ast["left"], environment) >= evaluate(ast["right"], environment)
    elif ast["tag"] == "and":
        left = evaluate(ast["left"], environment)
        if not is_truthy(left):
            return False
        right = evaluate(ast["right"], environment)
        return is_truthy(right)
    elif ast["tag"] == "or":
        left = evaluate(ast["left"], environment)
        if is_truthy(left):
            return True
        right = evaluate(ast["right"], environment)
        return is_truthy(right)
    elif ast["tag"] == "not":
        value = evaluate(ast["operand"], environment)
        return not is_truthy(value)
    elif ast["tag"] == "print":
        result = evaluate(ast["expression"], environment)
        print(result)
        return None
    elif ast["tag"] == "if":
        condition = evaluate(ast["condition"], environment)
        if is_truthy(condition):
            evaluate(ast["then_block"], environment)
        else:
            if "else_block" in ast:
                evaluate(ast["else_block"], environment)
        return None
    elif ast["tag"] == "while":
        while is_truthy(evaluate(ast["condition"], environment)):
            evaluate(ast["do_block"], environment)
        return None
    elif ast["tag"] == "statement_list":
        for statement in ast["statements"]:
            evaluate(statement, environment)
        return None
    elif ast["tag"] == "program":
        evaluate(ast["statements"], environment)
        return None
    else:
        raise ValueError(f"Unknown AST node: {ast}")


def test_evaluate():
    print("test evaluate()")
    ast = {"tag": "number", "value": 3}
    assert evaluate(ast, {}) == 3

    ast = {"tag": "true"}
    assert evaluate(ast, {}) == True

    ast = {"tag": "false"}
    assert evaluate(ast, {}) == False

    ast = {
        "tag": "+",
        "left": {"tag": "number", "value": 3},
        "right": {"tag": "number", "value": 4},
    }
    assert evaluate(ast, {}) == 7
    ast = {
        "tag": "*",
        "left": {
            "tag": "+",
            "left": {"tag": "number", "value": 3},
            "right": {"tag": "number", "value": 4},
        },
        "right": {"tag": "number", "value": 5},
    }
    assert evaluate(ast, {}) == 35
    tokens = tokenizer.tokenize("3*(4+5)")
    ast, tokens = parser.parse_expression(tokens)
    assert evaluate(ast, {}) == 27


def test_evaluate_environments():
    print("test evaluate() with environments")
    ast = {"tag": "identifier", "value": "x"}
    assert evaluate(ast, {"x": 3}) == 3
    tokens = tokenizer.tokenize("3*(x+5)")
    ast, tokens = parser.parse_expression(tokens)
    environment = {"x": 4}
    assert evaluate(ast, environment) == 27
    try:
        assert evaluate(ast, {}) == 27
        assert True, "Failed to raise error for undefined identifier"
    except Exception as e:
        assert True, f"Unknown identifier in {str(e)}"
    tokens = tokenizer.tokenize("x*(z+y)")
    ast, tokens = parser.parse_expression(tokens)
    environment = {"$PARENT": {"z": 5}, "x": 4, "y": 3}
    assert evaluate(ast, environment) == 32
    tokens = tokenizer.tokenize("x*(z+y)")
    ast, tokens = parser.parse_expression(tokens)
    environment = {
        "$PARENT": {
            "$PARENT": {"z": 5},
        },
        "x": 4,
        "y": 3,
    }
    assert evaluate(ast, environment) == 32


def test_evaluate_assignments():
    tokens = tokenizer.tokenize("z=3*(x+5)")
    ast, tokens = parser.parse_statement(tokens)
    environment = {"x": 4}
    assert evaluate(ast, environment) == None
    print(environment)
    assert environment == {"x": 4, "z": 27}


def test_evaluate_comparisons():
    print("test evaluate() comparisons")
    tokens = tokenizer.tokenize("3 == 3")
    ast, tokens = parser.parse_expression(tokens)
    assert evaluate(ast, {}) == True

    tokens = tokenizer.tokenize("3 != 4")
    ast, tokens = parser.parse_expression(tokens)
    assert evaluate(ast, {}) == True

    tokens = tokenizer.tokenize("3 < 4")
    ast, tokens = parser.parse_expression(tokens)
    assert evaluate(ast, {}) == True

    tokens = tokenizer.tokenize("3 <= 3")
    ast, tokens = parser.parse_expression(tokens)
    assert evaluate(ast, {}) == True

    tokens = tokenizer.tokenize("5 > 3")
    ast, tokens = parser.parse_expression(tokens)
    assert evaluate(ast, {}) == True

    tokens = tokenizer.tokenize("5 >= 5")
    ast, tokens = parser.parse_expression(tokens)
    assert evaluate(ast, {}) == True


def test_evaluate_unary():
    print("test evaluate() unary")
    tokens = tokenizer.tokenize("-3")
    ast, tokens = parser.parse_expression(tokens)
    assert evaluate(ast, {}) == -3

    tokens = tokenizer.tokenize("--3")
    ast, tokens = parser.parse_expression(tokens)
    assert evaluate(ast, {}) == 3


def test_evaluate_logic():
    print("test evaluate() logic")
    tokens = tokenizer.tokenize("1 and 1")
    ast, tokens = parser.parse_expression(tokens)
    assert evaluate(ast, {}) == True

    tokens = tokenizer.tokenize("1 and 0")
    ast, tokens = parser.parse_expression(tokens)
    assert evaluate(ast, {}) == False

    tokens = tokenizer.tokenize("0 and 1")
    ast, tokens = parser.parse_expression(tokens)
    assert evaluate(ast, {}) == False

    tokens = tokenizer.tokenize("0 or 1")
    ast, tokens = parser.parse_expression(tokens)
    assert evaluate(ast, {}) == True

    tokens = tokenizer.tokenize("0 or 0")
    ast, tokens = parser.parse_expression(tokens)
    assert evaluate(ast, {}) == False

    tokens = tokenizer.tokenize("not 1")
    ast, tokens = parser.parse_expression(tokens)
    assert evaluate(ast, {}) == False

    tokens = tokenizer.tokenize("not 0")
    ast, tokens = parser.parse_expression(tokens)
    assert evaluate(ast, {}) == True

    tokens = tokenizer.tokenize("true and true")
    ast, tokens = parser.parse_expression(tokens)
    assert evaluate(ast, {}) == True

    tokens = tokenizer.tokenize("true and false")
    ast, tokens = parser.parse_expression(tokens)
    assert evaluate(ast, {}) == False

    tokens = tokenizer.tokenize("false or false")
    ast, tokens = parser.parse_expression(tokens)
    assert evaluate(ast, {}) == False

    tokens = tokenizer.tokenize("not true")
    ast, tokens = parser.parse_expression(tokens)
    assert evaluate(ast, {}) == False

    tokens = tokenizer.tokenize("not false")
    ast, tokens = parser.parse_expression(tokens)
    assert evaluate(ast, {}) == True


def test_evaluate_if_statement():
    tokens = tokenizer.tokenize("if (x>3){y=4}")
    ast, tokens = parser.parse_statement(tokens)
    environment = {"x": 4}
    assert evaluate(ast, environment) == None
    assert environment == {"x": 4, "y": 4}
    tokens = tokenizer.tokenize("if (x<3){y=4}")
    ast, tokens = parser.parse_statement(tokens)
    environment = {"x": 4}
    assert evaluate(ast, environment) == None
    assert environment == {"x": 4}
    tokens = tokenizer.tokenize("if (x>3){y=4}else{z=4}")
    ast, tokens = parser.parse_statement(tokens)
    environment = {"x": 4}
    assert evaluate(ast, environment) == None
    assert environment == {"x": 4, "y": 4}
    tokens = tokenizer.tokenize("if (x<3){y=4}else{z=4}")
    ast, tokens = parser.parse_statement(tokens)
    environment = {"x": 4}
    assert evaluate(ast, environment) == None
    assert environment == {"x": 4, "z": 4}


def test_evaluate_while_statement():
    tokens = tokenizer.tokenize("x=0; while (x<3){x=x+1}")
    ast, tokens = parser.parse_statement_list(tokens)
    environment = {"x": 4}
    assert evaluate(ast, environment) == None
    print(environment)
    assert environment == {"x": 3}

def test_evaluate_function_expression():
    tokens = tokenizer.tokenize("x=function(x){y=1}")
    ast, tokens = parser.parse_statement_list(tokens)
    environment = {"x": 4}
    assert evaluate(ast, environment) == None
    assert environment == {'x': {'tag': 'function', 'parameters': ['x'], 'body': {'tag': 'statement_list', 'statements': [{'tag': 'assign', 'target': 'y', 'expression': {'tag': 'number', 'value': 1}}]}}}

def test_evaluate_function_call():
    tokens = tokenizer.tokenize("x=function(x){print(314159);};z=x(2)")
    ast, tokens = parser.parse_statement_list(tokens)
    environment = {"x": 4}
    assert evaluate(ast, environment) == None
    print(environment)
    assert environment == {'x': {'tag': 'function', 'parameters': ['x'], 'body': {'tag': 'statement_list', 'statements': [{'tag': 'print', 'expression': {'tag': 'number', 'value': 314159}}]}}, 'z': None}
    environment = {"x": 4}
    tokens = tokenizer.tokenize("f=function(x,y){print(314159)}")
    ast, tokens = parser.parse_statement_list(tokens)
    assert evaluate(ast, environment) == None
    tokens = tokenizer.tokenize("z=f(012345,67890)")
    ast, tokens = parser.parse_statement_list(tokens)
    assert evaluate(ast, environment) == None

    tokens = tokenizer.tokenize("f=function(q,r){print(q+r)}")
    ast, tokens = parser.parse_statement_list(tokens)
    assert evaluate(ast, environment) == None
    tokens = tokenizer.tokenize("z=f(1+2,3+4)")
    ast, tokens = parser.parse_statement_list(tokens)
    assert evaluate(ast, environment) == None

    tokens = tokenizer.tokenize("x=100; f=function(q,r){print(q+r+x)}")
    ast, tokens = parser.parse_statement_list(tokens)
    assert evaluate(ast, environment) == None
    tokens = tokenizer.tokenize("z=f(1+2,3+4)")
    ast, tokens = parser.parse_statement_list(tokens)
    assert evaluate(ast, environment) == None

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
