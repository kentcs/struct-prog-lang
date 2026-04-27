from tokenizer import tokenize
from parser import parse
from pprint import pprint
import copy
import errors


def type_of(*args):
    def single_type(x):
        if isinstance(x, bool):
            return "boolean"
        if isinstance(x, int) or isinstance(x, float):
            return "number"
        if isinstance(x, str):
            return "string"
        if isinstance(x, list):
            return "array"
        if isinstance(x, dict):
            return "object"
        if x is None:
            return "null"
        assert False, f"Unknown type for value: {x}"

    return "-".join(single_type(arg) for arg in args)


def is_truthy(x):
    if x in [None, False, 0, 0.0, ""]:
        return False
    if isinstance(x, (list, dict)) and len(x) == 0:
        return False
    return True


def ast_to_string(ast):
    s = ""
    if ast["tag"] == "number":
        return str(ast["value"])
    if ast["tag"] == "string":
        return str('"' + ast["value"] + '"')
    if ast["tag"] == "boolean":  # Added for completeness
        return "true" if ast["value"] else "false"
    if ast["tag"] == "null":
        return "null"
    if ast["tag"] == "list":
        items = []
        for item in ast["items"]:
            result = ast_to_string(item)
            items.append(result)
        return "[" + ",".join(items) + "]"
    if ast["tag"] == "object":
        items = []
        for item in ast["items"]:
            key = ast_to_string(item["key"])
            value = ast_to_string(item["value"])
            items.append(f"{key}:{value}")
        return "{" + ",".join(items) + "}"
    if ast["tag"] == "identifier":
        return str(ast["value"])
    if ast["tag"] in [
        "+",
        "-",
        "/",
        "*",
        "%",
        "&&",
        "||",
        "and",
        "or",
        "<",
        ">",
        "<=",
        ">=",
        "==",
        "!=",
    ]:
        return (
            "("
            + ast_to_string(ast["left"])
            + ast["tag"]
            + ast_to_string(ast["right"])
            + ")"
        )
    if ast["tag"] in ["negate"]:
        return "(-" + ast_to_string(ast["value"]) + ")"
    if ast["tag"] in ["not", "!"]:
        return "(" + ast["tag"] + " " + ast_to_string(ast["value"]) + ")"
    if ast["tag"] == "print":
        if "value" in ast and ast["value"] is not None:
            return "print (" + ast_to_string(ast["value"]) + ")"
        else:
            return "print ()"

    if ast["tag"] == "assert":
        s = "assert (" + ast_to_string(ast["condition"]) + ")"
        if "explanation" in ast and ast["explanation"]:  # Check existence
            s = s + ", " + ast_to_string(ast["explanation"])  # Added space
        return s  # Return s here

    if ast["tag"] == "if":
        s = (
            "if ("
            + ast_to_string(ast["condition"])
            + ") {"
            + ast_to_string(ast["then"])
            + "}"
        )
        if "else" in ast and ast["else"]:  # Check existence
            s = s + " else {" + ast_to_string(ast["else"]) + "}"
        return s

    if ast["tag"] == "while":
        s = (
            "while ("
            + ast_to_string(ast["condition"])
            + ") {"
            + ast_to_string(ast["do"])
            + "}"
        )

    if ast["tag"] == "statement_list":
        items = []
        for item in ast["statements"]:
            result = ast_to_string(item)
            items.append(result)
        return "{" + ";".join(items) + "}"

    if ast["tag"] == "program":
        items = []
        for item in ast["statements"]:
            result = ast_to_string(item)
            items.append(result)
        return "{" + ";".join(items) + "}"

    if ast["tag"] == "function":
        return str(ast)

    if ast["tag"] == "call":
        items = []
        for item in ast["arguments"]:
            result = ast_to_string(item)
            items.append(result)
        # Include function name for clarity
        return ast_to_string(ast["function"]) + "(" + ",".join(items) + ")"

    if ast["tag"] == "complex":
        s = f"{ast_to_string(ast["base"])}[{ast_to_string(ast["index"])}]"
        return s

    if ast["tag"] == "assign":
        extern_prefix = "extern " if ast["target"].get("extern") else ""
        s = f"{extern_prefix}{ast_to_string(ast['target'])} = {ast_to_string(ast['value'])}"  # Removed extra ]
        return s

    if ast["tag"] == "return":
        if "value" in ast and ast["value"] is not None:  # Check existence and not None
            return "return " + ast_to_string(ast["value"])
        else:
            return "return"

    # Add missing AST node types for ast_to_string completeness
    if ast["tag"] == "exit":
        if "value" in ast and ast["value"] is not None:
            return "exit " + ast_to_string(ast["value"])
        return "exit"
    if ast["tag"] == "break":
        return "break"
    if ast["tag"] == "continue":
        return "continue"
    if ast["tag"] == "import":
        return "import " + ast_to_string(ast["value"])

    assert False, f"Unknown tag [{ast['tag']}] in AST"


# Builtins are recognized in identifier lookup and dispatched in function calls.
__builtin_functions = ["head", "tail", "length", "keys", "input"]


def evaluate_builtin_function(function_name, args):
    # List helper builtins for topic 08.
    if function_name == "head":
        assert len(args) == 1 and isinstance(
            args[0], list
        ), "head() requires a single list argument"
        return (args[0][0] if args[0] else None), None

    if function_name == "tail":
        assert len(args) == 1 and isinstance(
            args[0], list
        ), "tail() requires a single list argument"
        return args[0][1:], None

    if function_name == "length":
        assert len(args) == 1 and isinstance(
            args[0], (list, dict, str)
        ), "length() requires list, object, or string"
        return len(args[0]), None

    if function_name == "keys":
        assert len(args) == 1 and isinstance(
            args[0], dict
        ), "keys() requires an object argument"
        return list(args[0].keys()), None

    if function_name == "input":
        assert len(args) == 0, "input() requires no arguments"
        return input(), None  # Uses Python's built-in input()

    assert False, f"Unknown builtin function '{function_name}'"


def evaluate(ast, environment):
    if ast["tag"] == "number":
        assert type(ast["value"]) in [
            float,
            int,
        ], f"unexpected type {type(ast["value"])}"
        return ast["value"], None
    if ast["tag"] == "boolean":
        assert ast["value"] in [
            True,
            False,
        ], f"unexpected type {type(ast["value"])}"
        return ast["value"], None
    if ast["tag"] == "string":
        assert type(ast["value"]) == str, f"unexpected type {type(ast["value"])}"
        return ast["value"], None
    if ast["tag"] == "null":
        return None, None
    if ast["tag"] == "list":
        items = []
        for item in ast["items"]:
            result, item_status = evaluate(item, environment)
            if item_status == "exit":  # Propagate exit if an item evaluation causes it
                return result, "exit"
            items.append(result)
        return items, None
    if ast["tag"] == "object":
        object = {}
        for item in ast["items"]:
            key, key_status = evaluate(item["key"], environment)
            if key_status == "exit":
                return key, "exit"
            assert type(key) is str, "Object key must be a string"
            value, value_status = evaluate(item["value"], environment)
            if value_status == "exit":
                return value, "exit"
            object[key] = value
        return object, None

    if ast["tag"] == "identifier":
        identifier = ast["value"]
    if identifier in environment:
        return environment[identifier], None
    if "$parent" in environment:
        return evaluate(ast, environment["$parent"])
    # Unbound names are checked against builtin functions before failing.
    if identifier in __builtin_functions:
        return {"tag": "builtin", "name": identifier}, None
        raise Exception(f"Unknown identifier: '{identifier}'")

    if ast["tag"] == "+":
        left_value, l_status = evaluate(ast["left"], environment)
        if l_status == "exit":
            return left_value, "exit"
        right_value, r_status = evaluate(ast["right"], environment)
        if r_status == "exit":
            return right_value, "exit"
        types = type_of(left_value, right_value)
        if types == "number-number":
            return left_value + right_value, None
        if types == "string-string":
            return left_value + right_value, None
        if types == "object-object":
            # Ensure no deepcopy issues if objects contain shared mutable structures from environment
            return {**copy.deepcopy(left_value), **copy.deepcopy(right_value)}, None
        if types == "array-array":
            return copy.deepcopy(left_value) + copy.deepcopy(right_value), None
        raise Exception(f"Illegal types for {ast['tag']}: {types}")
    if ast["tag"] == "-":
        left_value, l_status = evaluate(ast["left"], environment)
        if l_status == "exit":
            return left_value, "exit"
        right_value, r_status = evaluate(ast["right"], environment)
        if r_status == "exit":
            return right_value, "exit"
        types = type_of(left_value, right_value)
        if types == "number-number":
            return left_value - right_value, None
        raise Exception(f"Illegal types for {ast["tag"]}:{types}")

    if ast["tag"] == "*":
        left_value, l_status = evaluate(ast["left"], environment)
        if l_status == "exit":
            return left_value, "exit"
        right_value, r_status = evaluate(ast["right"], environment)
        if r_status == "exit":
            return right_value, "exit"
        types = type_of(left_value, right_value)
        if types == "number-number":
            return left_value * right_value, None
        if types == "string-number":
            return left_value * int(right_value), None
        if types == "number-string":
            return int(left_value) * right_value, None  # Corrected order
        raise Exception(f"Illegal types for {ast['tag']}:{types}")

    if ast["tag"] == "/":
        left_value, l_status = evaluate(ast["left"], environment)
        if l_status == "exit":
            return left_value, "exit"
        right_value, r_status = evaluate(ast["right"], environment)
        if r_status == "exit":
            return right_value, "exit"
        types = type_of(left_value, right_value)
        if types == "number-number":
            errors.check(
                right_value != 0,
                "Division by zero",
                line=ast.get("line"),
                column=ast.get("column"),
            )
            return left_value / right_value, None
        raise Exception(f"Illegal types for {ast['tag']}:{types}")
    if ast["tag"] == "%":
        left_value, l_status = evaluate(ast["left"], environment)
        if l_status == "exit":
            return left_value, "exit"
        right_value, r_status = evaluate(ast["right"], environment)
        if r_status == "exit":
            return right_value, "exit"
        types = type_of(left_value, right_value)
        if types == "number-number":
            errors.check(
                right_value != 0,
                "Modulo by zero",
                line=ast.get("line"),
                column=ast.get("column"),
            )
            return left_value % right_value, None
        raise Exception(f"Illegal types for {ast['tag']}:{types}")

    if ast["tag"] == "negate":
        value, status = evaluate(ast["value"], environment)
        if status == "exit":
            return value, "exit"
        types = type_of(value)
        if types == "number":
            return -value, None
        raise Exception(f"Illegal type for {ast['tag']}:{types}")

    if ast["tag"] in ["&&", "and"]:
        left_value, l_status = evaluate(ast["left"], environment)
        if l_status == "exit":
            return left_value, "exit"
        # Short-circuit evaluation for 'and'
        if not is_truthy(left_value):
            return (
                left_value,
                None,
            )  # Or False, depending on desired semantics for 'and'
        right_value, r_status = evaluate(ast["right"], environment)
        if r_status == "exit":
            return right_value, "exit"
        return is_truthy(left_value) and is_truthy(right_value), None

    if ast["tag"] in ["||", "or"]:
        left_value, l_status = evaluate(ast["left"], environment)
        if l_status == "exit":
            return left_value, "exit"
        # Short-circuit evaluation for 'or'
        if is_truthy(left_value):
            return left_value, None  # Or True, depending on desired semantics for 'or'
        right_value, r_status = evaluate(ast["right"], environment)
        if r_status == "exit":
            return right_value, "exit"
        return is_truthy(left_value) or is_truthy(right_value), None

    if ast["tag"] in ["!", "not"]:
        value, status = evaluate(ast["value"], environment)
        if status == "exit":
            return value, "exit"
        return not is_truthy(value), None

    if ast["tag"] in ["<", ">", "<=", ">="]:
        left_value, l_status = evaluate(ast["left"], environment)
        if l_status == "exit":
            return left_value, "exit"
        right_value, r_status = evaluate(ast["right"], environment)
        if r_status == "exit":
            return right_value, "exit"
        types = type_of(left_value, right_value)
        if types not in ["number-number", "string-string"]:
            raise Exception(f"Illegal types for {ast['tag']}: {types}")
        if ast["tag"] == "<":
            return left_value < right_value, None
        if ast["tag"] == ">":
            return left_value > right_value, None
        if ast["tag"] == "<=":
            return left_value <= right_value, None
        if ast["tag"] == ">=":
            return left_value >= right_value, None

    if ast["tag"] == "==":
        left_value, l_status = evaluate(ast["left"], environment)
        if l_status == "exit":
            return left_value, "exit"
        right_value, r_status = evaluate(ast["right"], environment)
        if r_status == "exit":
            return right_value, "exit"
        return left_value == right_value, None

    if ast["tag"] == "!=":
        left_value, l_status = evaluate(ast["left"], environment)
        if l_status == "exit":
            return left_value, "exit"
        right_value, r_status = evaluate(ast["right"], environment)
        if r_status == "exit":
            return right_value, "exit"
        return left_value != right_value, None

    if ast["tag"] == "print":
        if ast["value"]:
            value, status = evaluate(ast["value"], environment)
            if status == "exit":
                return value, "exit"
            if type(value) is bool:
                if value == True:
                    value = "true"
                if value == False:
                    value = "false"
            print(str(value))
            return str(value) + "\n", None  # Return the printed value with newline
        else:
            print()
        return "\n", None  # Print with no args returns a newline string

    if ast["tag"] == "assert":
        if ast["condition"]:
            condition_value, cond_status = evaluate(ast["condition"], environment)
            if cond_status == "exit":
                return condition_value, "exit"
            if not is_truthy(condition_value):
                error_msg = f"Assertion failed: {ast_to_string(ast['condition'])}"
                if "explanation" in ast and ast["explanation"]:
                    explanation_val, expl_status = evaluate(
                        ast["explanation"], environment
                    )
                    if expl_status == "exit":
                        return explanation_val, "exit"
                    error_msg += f" ({explanation_val})"
                raise Exception(error_msg)
        return None, None  # Assert statement itself doesn't produce a value

    if ast["tag"] == "if":
        condition_value, cond_status = evaluate(ast["condition"], environment)
        if cond_status == "exit":
            return condition_value, "exit"

        if is_truthy(condition_value):
            val, status = evaluate(ast["then"], environment)
            if status:  # Propagate "return", "exit", "break", "continue"
                return val, status
        else:
            if "else" in ast:
                val, status = evaluate(ast["else"], environment)
                if status:  # Propagate "return", "exit", "break", "continue"
                    return val, status
        return None, None  # Normal completion of if/else

    if ast["tag"] == "while":
        # Condition is evaluated in the current environment
        condition_value, cond_status = evaluate(ast["condition"], environment)
        if cond_status == "exit":
            return condition_value, "exit"

        while is_truthy(condition_value):
            val, body_status = evaluate(ast["do"], environment)

            if body_status == "return" or body_status == "exit":
                return val, body_status  # Propagate critical exits
            if body_status == "break":
                break  # Exit the while loop, loop completes normally
            if body_status == "continue":
                # Re-evaluate condition and continue to next iteration
                condition_value, cond_status = evaluate(ast["condition"], environment)
                if cond_status == "exit":
                    return condition_value, "exit"
                continue  # Continue to next iteration of while

            # If body completed normally (status is None), re-evaluate condition
            condition_value, cond_status = evaluate(ast["condition"], environment)
            if cond_status == "exit":
                return condition_value, "exit"
        return None, None  # Normal loop termination (condition false or break occurred)

    if ast["tag"] == "statement_list":
        last_value = None
        for statement in ast["statements"]:
            last_value, status = evaluate(statement, environment)
            if status:  # "return", "exit", "break", "continue"
                return last_value, status
        return last_value, None  # All statements completed normally

    if ast["tag"] == "program":
        last_value = None
        for statement in ast["statements"]:
            val, status = evaluate(statement, environment)
            if status:
                if status == "return":
                    raise Exception("'return' statement outside of function.")
                if status in ["break", "continue"]:
                    raise Exception(f"'{status}' statement outside of loop.")
                return val, status  # Propagate "exit"
            last_value = val
        return last_value, None  # Program completed normally

    if ast["tag"] == "function":
        return {
            "tag": "function",
            "parameters": ast["parameters"],
            "body": ast["body"],
            "environment": environment,
        }, None  # Function definition itself is a normal evaluation

    if ast["tag"] == "call":
        function, func_status = evaluate(ast["function"], environment)
        if func_status == "exit":
            return function, "exit"
        argument_values = []
        for arg in ast["arguments"]:
            arg_val, arg_status = evaluate(arg, environment)
            if arg_status == "exit":
                return arg_val, "exit"
            argument_values.append(arg_val)
        # Builtins are handled directly; regular functions use the local environment path below.
        if function.get("tag") == "builtin":
            return evaluate_builtin_function(function["name"], argument_values)

        # regular function call:
        local_environment = {
            name["value"]: val
            for name, val in zip(function["parameters"], argument_values)
        }
        local_environment["$parent"] = function["environment"]
        val, status = evaluate(function["body"], local_environment)

        if status == "return":
            return val, None  # Consume "return" status, call evaluates to the value
        elif status == "exit":
            return val, "exit"  # Propagate "exit"
        elif status in [
            "break",
            "continue",
        ]:  # Should not happen if loops/program node are correct
            raise Exception(f"'{status}' statement outside of loop.")
        else:  # Normal function completion without explicit return (status is None)
            return None, None

    if ast["tag"] == "complex":
        base, base_status = evaluate(ast["base"], environment)
        if base_status == "exit":
            return base, "exit"
        index, index_status = evaluate(ast["index"], environment)
        if index_status == "exit":
            return index, "exit"

        if index is None:  # index evaluated to null
            raise Exception(
                f"TypeError: Cannot index with 'null'. Base: {base}, Index AST: {ast_to_string(ast['index'])}"
            )
        if type(index) in [int, float]:
            assert int(index) == index
            assert type(base) == list
            if not (0 <= index < len(base)):
                raise IndexError("List index out of range")
            return base[index], None
        if type(index) == str:
            assert type(base) == dict
            if index not in base:
                raise KeyError(f"Key '{index}' not found in object")
            return base[index], None
        assert False, f"Unknown index type [{index}]"

    if ast["tag"] == "assign":
        assert "target" in ast
        target = ast["target"]

        if target["tag"] == "identifier":
            name = target["value"]

            if target.get("extern"):
                scope = environment
                while scope is not None and name not in scope:
                    scope = scope.get("$parent")
                assert (
                    scope is not None
                ), f"Extern assignment: '{name}' not found in any outer scope"
                target_base = scope
            else:
                # Always assign to local scope
                target_base = environment

            target_index = name

        elif target["tag"] == "complex":
            base, base_status = evaluate(target["base"], environment)
            if base_status == "exit":
                return base, "exit"
            index_ast = target["index"]

            if index_ast["tag"] == "string":
                index = index_ast["value"]
            else:
                index, index_status = evaluate(index_ast, environment)
                if index_status == "exit":
                    return index, "exit"

            if index is None:
                raise Exception("Cannot use 'null' as index for assignment.")
            assert type(index) in [int, float, str], f"Unknown index type [{index}]"

            if isinstance(base, list):
                assert isinstance(index, int), "List index must be integer"
                assert 0 <= index < len(base), "List index out of range"
                target_base = base
                target_index = index
            elif isinstance(base, dict):
                target_base = base
                target_index = index
            else:
                assert False, f"Cannot assign to base of type {type(base)}"

        value, value_status = evaluate(ast["value"], environment)
        if value_status == "exit":
            return value, "exit"

        target_base[target_index] = value
        return value, None

    if ast["tag"] == "return":
        if (
            "value" in ast and ast["value"] is not None
        ):  # Checks if 'return' has an expression
            evaluated_value, expression_status = evaluate(ast["value"], environment)
            if expression_status == "exit":  # If the expression itself caused an exit
                return (
                    evaluated_value,
                    "exit",
                )  # Propagate the exit status and its value
            # Otherwise, the expression evaluated normally or had another status.
            # The 'return' statement now imposes its "return" status.
            return evaluated_value, "return"
        return None, "return"

    if ast["tag"] == "exit":
        exit_code = 0  # Default exit code
        if "value" in ast and ast["value"] is not None:
            exit_code_val, status = evaluate(ast["value"], environment)
            if status == "exit":
                return exit_code_val, "exit"  # if expr itself exits
            assert isinstance(exit_code_val, int), "Exit code must be an integer."
            return exit_code_val, "exit"
        return exit_code, "exit"

    if ast["tag"] == "break":
        return None, "break"

    if ast["tag"] == "continue":
        return None, "continue"

    if ast["tag"] == "import":
        filename_val, status = evaluate(ast["value"], environment)
        if status == "exit":
            return filename_val, "exit"
        assert isinstance(filename_val, str), "Import path must be a string."
        # Basic import logic (can be expanded for caching, namespaces, etc.)
        try:
            with open(filename_val, "r") as f:
                source_code = f.read()
            imported_tokens = tokenize(source_code)
            imported_ast = parse(imported_tokens)
            # Evaluate in the current environment.
            return evaluate(
                imported_ast, environment
            )  # Propagates value and status from imported code
        except FileNotFoundError:
            raise Exception(f"ImportError: File not found '{filename_val}'")
        except Exception as e:
            raise Exception(f"Error during import of '{filename_val}': {e}")

    assert False, f"Unknown tag [{ast['tag']}] in AST"


def clean(e):
    if type(e) is dict:
        return {
            k: clean(v)
            for k, v in e.items()
            if k not in ("environment", "line", "column", "position")
        }
    if type(e) is list:
        return [clean(v) for v in e]
    else:
        return e


def equals(code, environment, expected_result, expected_environment=None):
    result, status = evaluate(parse(tokenize(code)), environment)

    assert clean(result) == clean(expected_result), f"""ERROR: When executing
    {[code]} 
    -- expected result -- 
    {[expected_result]}
    -- got --
    {[result]}."""
    assert (
        status is None or status == "exit"
    ), f"Test case '{code}' ended with unexpected status '{status}'"

    if expected_environment != None:
        assert clean(environment) == clean(
            expected_environment
        ), f"""ERROR: When executing
        {[code]} 
        -- expected environment -- 
        {[(expected_environment)]}
        -- got --
        {[(environment)]}."""


def test_evaluate_single_value():
    print("test evaluate single value")
    equals("4", {}, 4, {})
    equals("3", {}, 3, {})
    equals("4.2", {}, 4.2, {})
    equals("X", {"X": 1}, 1)
    equals("Y", {"X": 1, "Y": 2}, 2)
    equals('"x"', {"x": "cat", "y": 2}, "x")
    equals("x", {"x": "cat", "y": 2}, "cat")
    equals("null", {}, None)


def test_evaluate_addition():
    print("test evaluate addition")
    equals("1+1", {}, 2, {})
    equals("1+2+3", {}, 6, {})
    equals("1.2+2.3+3.4", {}, 6.9, {})
    equals("X+Y", {"X": 1, "Y": 2}, 3)
    equals('"X"+"Y"', {}, "XY")


def test_evaluate_subtraction():
    print("test evaluate subtraction")
    equals("1-1", {}, 0, {})
    equals("3-2-1", {}, 0, {})


def test_evaluate_multiplication():
    print("test evaluate multiplication")
    equals("1*1", {}, 1, {})
    equals("3*2*2", {}, 12, {})
    equals("3+2*2", {}, 7, {})
    equals("(3+2)*2", {}, 10, {})


def test_evaluate_division():
    print("test evaluate division")
    equals("4/2", {}, 2, {})
    equals("8/4/2", {}, 1, {})


def test_evaluate_negation():
    print("test evaluate negation")
    equals("-2", {}, -2, {})
    equals("--3", {}, 3, {})


def test_evaluate_print_statement():
    print("test evaluate_print_statement")
    equals("print", {}, "\n", {})
    equals("print 1", {}, "1\n", {})
    equals("print 1+1", {}, "2\n", {})
    equals("print 1+1+1", {}, "3\n", {})
    equals("print true", {}, "true\n", {})
    equals("print false", {}, "false\n", {})


def test_evaluate_if_statement():
    print("testing evaluate_if_statement")
    equals("if(1) {3}", {}, None, {})
    equals("if(0) {3}", {}, None, {})
    equals("if(1) {x=1}", {"x": 0}, None, {"x": 1})
    equals("if(0) {x=1}", {"x": 0}, None, {"x": 0})
    equals("if(1) {x=1} else {x=2}", {"x": 0}, None, {"x": 1})
    equals("if(0) {x=1} else {x=2}", {"x": 0}, None, {"x": 2})


def test_evaluate_while_statement():
    print("testing evaluate_while_statement")
    equals("while(0) {x=1}", {}, None, {})
    equals("x=1; while(x<5) {x=x+1}; y=3", {}, 3, {"x": 5, "y": 3})


def test_evaluate_assignment_statement():
    print("test evaluate_assignment_statement")
    equals("X=1", {}, 1, {"X": 1})
    equals("x=x+1", {"x": 1}, 2, {"x": 2})
    equals("y=x+1", {"y": 1, "$parent": {"x": 3}}, 4, {"y": 4, "$parent": {"x": 3}})
    equals(
        "x=x+1",
        {"y": 1, "$parent": {"x": 3}},
        4,
        {"y": 1, "x": 4, "$parent": {"x": 3}},
    )


def test_evaluate_list_literal():
    print("test evaluate_list_literal")
    environment = {}
    code = "[1,2,3]"
    ast = parse(tokenize(code))
    result, _ = evaluate(ast, environment)
    assert result == [1, 2, 3]
    code = "[]"
    ast = parse(tokenize(code))
    result, _ = evaluate(ast, environment)
    assert result == []


def test_evaluate_object_literal():
    print("test evaluate_object_literal")
    environment = {}
    code = '{"a":1,"b":2}'
    ast = parse(tokenize(code))
    result, _ = evaluate(ast, environment)
    assert result == {"a": 1, "b": 2}
    code = "{}"
    ast = parse(tokenize(code))
    result, _ = evaluate(ast, environment)
    assert result == {}


def test_evaluate_function_literal():
    print("test evaluate_function_literal")
    code = "f=function(x) {1}"
    ast = parse(tokenize(code))
    equals(
        code,
        {},
        {
            "tag": "function",
            "parameters": [{"tag": "identifier", "value": "x"}],
            "body": {
                "tag": "statement_list",
                "statements": [{"tag": "number", "value": 1}],
            },
        },
        {
            "f": {
                "tag": "function",
                "parameters": [{"tag": "identifier", "value": "x"}],
                "body": {
                    "tag": "statement_list",
                    "statements": [{"tag": "number", "value": 1}],
                },
            }
        },
    )
    code = "function f(x) {1}"
    ast = parse(tokenize(code))
    equals(
        code,
        {},
        {
            "tag": "function",
            "parameters": [{"tag": "identifier", "value": "x"}],
            "body": {
                "tag": "statement_list",
                "statements": [{"tag": "number", "value": 1}],
            },
        },
        {
            "f": {
                "tag": "function",
                "parameters": [{"tag": "identifier", "value": "x"}],
                "body": {
                    "tag": "statement_list",
                    "statements": [{"tag": "number", "value": 1}],
                },
            }
        },
    )


def test_evaluate_function_call():
    print("test evaluate_function_call")
    environment = {}
    code = "function f() {return(1234)}"
    result, _ = evaluate(parse(tokenize(code)), environment)
    assert clean(environment) == {
        "f": {
            "tag": "function",
            "parameters": [],
            "body": {
                "tag": "statement_list",
                "statements": [
                    {"tag": "return", "value": {"tag": "number", "value": 1234}}
                ],
            },
        }
    }
    ast = parse(tokenize("f()"))
    assert ast == {
        "statements": [
            {
                "arguments": [],
                "function": {"tag": "identifier", "value": "f"},
                "tag": "call",
            }
        ],
        "tag": "program",
    }
    result, _ = evaluate(ast, environment)
    assert result == 1234
    environment = {}
    code = """
        x = 3; 
        function g(q)
            {return 2};
        g(4)
        """
    ast = parse(tokenize(code))
    result, _ = evaluate(ast, environment)
    assert result == 2
    code = """
        x = 3; 
        function g(q)
            {return [1,2,3,q]};
        g(4)
        """
    ast = parse(tokenize(code))
    result, _ = evaluate(ast, environment)
    assert result == [1, 2, 3, 4]


def test_evaluate_return_statement():
    print("test evaluate_return_statement")
    environment = {}
    code = """
        function f() { return };
        f()
    """
    result, _ = evaluate(parse(tokenize(code)), environment)
    assert result == None
    code = """
        function f() { return 2+2 };
        f()
    """
    result, _ = evaluate(parse(tokenize(code)), environment)
    assert result == 4
    code = """
        function f(x) { 
            if (x > 1) {
                return 123
            };
            return 2+2 
        };
        f(7) + f(0)
    """
    result, _ = evaluate(parse(tokenize(code)), environment)
    assert result == 127


def test_evaluate_complex_expression():
    print("test evaluate_complex_expression")
    environment = {"x": [2, 4, 6, 8]}
    code = "x[3]"
    ast = parse(tokenize(code))
    result, _ = evaluate(ast, environment)
    assert result == 8

    environment = {"x": {"a": 3, "b": 4}}
    code = 'x["b"]'
    ast = parse(tokenize(code))
    result, _ = evaluate(ast, environment)
    assert result == 4

    environment = {"x": {"a": [1, 2, 3], "b": 4}}
    code = 'x["a"]'
    ast = parse(tokenize(code))
    result, _ = evaluate(ast, environment)
    assert result == [1, 2, 3]

    code = 'x["a"][2]'
    ast = parse(tokenize(code))
    result, _ = evaluate(ast, environment)
    assert result == 3

    code = "x.a[2]"
    ast = parse(tokenize(code))
    result, _ = evaluate(ast, environment)
    assert result == 3
    code = "x.b = 7;"
    ast = parse(tokenize(code))
    result, _ = evaluate(ast, environment)
    code = "x.b;"
    ast = parse(tokenize(code))
    result, _ = evaluate(ast, environment)
    assert result == 7

    environment = {"x": [[1, 2], [3, 4]]}
    code = "x[0][1]"
    ast = parse(tokenize(code))
    result, _ = evaluate(ast, environment)
    assert result == 2

    environment = {"x": {"a": {"x": 4, "y": 6}, "b": {"x": 5, "y": 7}}}
    code = 'x["b"]["y"]'
    ast = parse(tokenize(code))
    result, _ = evaluate(ast, environment)
    assert result == 7


def test_evaluate_complex_assignment():
    print("test evaluate_complex_assignment")
    environment = {"x": [1, 2, 3]}
    code = "x[1]=4"
    ast = parse(tokenize(code))
    result, _ = evaluate(ast, environment)
    assert environment["x"][1] == 4

    environment = {"x": {"a": 1, "b": 2}}
    code = 'x["b"]=4'
    ast = parse(tokenize(code))
    result, _ = evaluate(ast, environment)
    assert environment["x"]["b"] == 4


def test_evaluate_builtins():
    print("test evaluate builtins")

    # head() returns the first list item, or null-ish empty-list behavior.
    # head of list
    equals("head([1,2,3])", {}, 1)
    equals("head([])", {}, None)

    # tail() returns the remainder of the list.
    # tail of list
    equals("tail([1,2,3])", {}, [2, 3])
    equals("tail([])", {}, [])

    # length() works for lists, strings, and objects.
    # length of list, string, object
    equals("length([1,2,3])", {}, 3)
    equals('length("hello")', {}, 5)
    equals("length({})", {}, 0)
    equals('length({"a":1,"b":2})', {}, 2)

    # keys() is still present here because topic 08 inherits the broader runtime.
    # keys of object
    equals('keys({"a":1,"b":2})', {}, ["a", "b"])
    equals("keys({})", {}, [])

    # input (mocking is tricky here, this just tests if it's recognized)
    # For a real test, you'd need to mock Python's input()
    # equals("input()", {}, "test_input_value") # This would require mocking


def test_evaluator_with_new_tags():
    print("test evaluator with new tags...")

    # test not / !
    equals("!0", {}, True)
    equals("not 0", {}, True)
    equals("!1", {}, False)
    equals("not 1", {}, False)

    # test and / &&
    equals("1 and 1", {}, True)
    equals("1 && 1", {}, True)
    equals("0 and 1", {}, False)
    equals("0 && 1", {}, False)

    # test or / ||
    equals("1 or 0", {}, True)
    equals("1 || 0", {}, True)
    equals("0 or 0", {}, False)
    equals("0 || 0", {}, False)

    # test assignment expressions
    env = {}
    equals("x=5", env, 5, {"x": 5})
    equals("y=x+2", env, 7, {"x": 5, "y": 7})

    # test nested assignment expressions
    env = {}
    equals("a=b=4", env, 4, {"a": 4, "b": 4})

    # test block with or without extra semicolons or bracket statements
    equals("if(1){x=1; y=2}", {}, None, {"x": 1, "y": 2})
    equals("if(1){x=1; y=2;}", {}, None, {"x": 1, "y": 2})
    equals("if(1){x=1; if(false) {z=4} y=2;}", {}, None, {"x": 1, "y": 2})


def test_scoping():
    print("test scoping")

    # Parent environment used in local assignment
    env = {"x": 10}
    code = "y = x + 5"
    equals(code, env, 15, {"x": 10, "y": 15})

    # Local variable assignment
    env = {}
    code = "x = 42"
    equals(code, env, 42, {"x": 42})

    # Local assignment does NOT affect parent
    env = {"x": 1}
    code = """
        function f() {
            x = 2
        };
        f()
    """
    # We don't care about the function's environment here, so we drop it
    result, _ = evaluate(parse(tokenize(code)), env)
    assert env["x"] == 1, "Local assignment should not affect parent scope"

    # External assignment does affect parent
    env = {}
    code = """
        x = 1;
        function f() {
            extern x = 2;
        };
        f()
    """
    result, _ = evaluate(parse(tokenize(code)), env)
    assert env["x"] == 2, "Extern assignment should affect parent scope"

    code = """
        x = 1;

        foo = function() {
            return x;
        };

        bar = function() {
            x = 2;
            return foo();
        };

        result = bar();
    """
    env = {}
    evaluate(parse(tokenize(code)), env)

    # foo should see outer x = 1, not the x = 2 inside bar
    assert env["result"] == 1, f"Expected result = 1, got {env['result']}"


def test_closures():
    print("test closures")

    code = """
        function makeCounter() {
            count = 0;
            return function() {
                extern count = count + 1;
                return count;
            };
        };
        c1 = makeCounter();
        c2 = makeCounter();
    """
    env = {}
    result, _ = evaluate(parse(tokenize(code)), env)

    # Now call c1() and c2() within the same env
    equals("c1()", env, 1)
    equals("c1()", env, 2)
    equals("c2()", env, 1)
    equals("c1()", env, 3)


def test_control_flow_scoping_rules():
    print("test control flow scoping rules")

    # Invalid return (caught by 'program' node)
    try:
        evaluate(parse(tokenize("return 1;")), {})
        assert False, "Top-level return should fail"
    except Exception as e:
        assert "'return' statement outside of function" in str(e)

    # Invalid break (caught by 'program' node)
    try:
        evaluate(parse(tokenize("break;")), {})
        assert False, "Top-level break should fail"
    except Exception as e:
        assert "'break' statement outside of loop" in str(e)

    # Invalid continue (caught by 'program' node)
    try:
        evaluate(parse(tokenize("continue;")), {})
        assert False, "Top-level continue should fail"
    except Exception as e:
        assert "'continue' statement outside of loop" in str(e)

    # Valid exit
    val, status = evaluate(parse(tokenize("exit 12;")), {})
    assert val == 12 and status == "exit"
    val, status = evaluate(parse(tokenize("exit;")), {})  # Default exit code 0
    assert val == 0 and status == "exit"

    # Return from within if, but not function (caught by 'program')
    try:
        evaluate(parse(tokenize("if(true){ return 1; }")), {})
        assert False, "Return inside if (not function) should fail at program level"
    except Exception as e:
        assert "'return' statement outside of function" in str(e)

    # Break from within function, but not loop (caught by 'program')
    code = "function f() { break; }; f();"
    try:
        evaluate(parse(tokenize(code)), {})
        assert False, "Break inside function (not loop) should fail at program level"
    except Exception as e:
        assert "'break' statement outside of loop" in str(e)


if __name__ == "__main__":
    # statements and programs are tested implicitly
    test_evaluate_single_value()
    test_evaluate_addition()
    test_evaluate_subtraction()
    test_evaluate_multiplication()
    test_evaluate_division()
    test_evaluate_negation()
    test_evaluate_print_statement()
    test_evaluate_if_statement()
    test_evaluate_while_statement()
    test_evaluate_assignment_statement()
    test_evaluate_function_literal()
    test_evaluate_function_call()
    test_evaluate_complex_expression()
    test_evaluate_complex_assignment()
    test_evaluate_return_statement()
    test_evaluate_list_literal()
    test_evaluate_object_literal()
    test_evaluate_builtins()
    test_evaluator_with_new_tags()
    test_scoping()
    test_closures()
    test_control_flow_scoping_rules()
    print("done.")
