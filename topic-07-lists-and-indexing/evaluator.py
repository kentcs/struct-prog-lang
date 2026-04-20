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


__builtin_functions = ["head", "tail", "length", "keys", "input"]


def evaluate_builtin_function(function_name, args):
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
        # Evaluate each element in order and build a Python list.
        # This is what makes list literals like [1, 2, 3] become actual values
        # at runtime instead of remaining as syntax trees.
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
        # Complex expressions are the runtime form for indexing.
        # Examples:
        #   x[0]
        #   x[1][2]
        #   nested["key"]
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
            # Indexed assignment updates an element inside a list or object.
            # For lists, the base must already evaluate to a list and the index
            # must be an integer. This is the list mutation path exercised by
            # the chapter 7 suite.
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

        ``
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











































