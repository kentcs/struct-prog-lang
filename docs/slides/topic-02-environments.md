# Statements and Environments

Building on expressions: programs, variables, and side effects.

---

## Extending Topic 01

Topic 01:
- Expressions
- Pure evaluation
- No memory
- No side effects

Topic 02:
- Statements
- Variables
- Side effects
- Programs

---

## Expressions vs Statements

Expressions:
- Compute a value
- Example: 3 + 4 -> 7

Statements:
- Perform an action
- May change program state
- Return no value

---

## Statements Return No Value

Statements execute.
They do not compute a usable result.

Example:

```
print 42
x = 10
```

Return value: None

---

## Programs

A program is a sequence of statements.

```
x = 10
y = 20
print x + y
```

Statements may be separated by semicolons:

```
print 1; print 2; print 3
```

---

## Environments (Symbol Tables)

An environment maps variable names to values.

Initially:

```
{}
```

As statements execute, the environment changes.

---

## Assignment Statements

Syntax:

```
<identifier> = <expression>
```

Examples:

```
x = 42
y = 3 + 4
```

---

## Assignment Evaluation

When evaluating:

```
x = 42
```

Steps:
1. Evaluate the right-hand expression
2. Store the result in the environment
3. Return None

Environment after:

```
{"x": 42}
```

---

## Assignment Step-by-Step

Program:

```
x = 10; y = 20; z = x + y
```

Execution:



```
After x = 10: {"x": 10}
After y = 20: {"x": 10, "y": 20}
After z = x + y:
- Lookup x -> 10
- Lookup y -> 20
- Compute 10 + 20 -> 30
-               {"x": 10, "y": 20, "z": 30}
```

---

## Using Variables in Expressions

```
x = 5
y = x + 3
```

Execution:
- `x = 5` -> {"x": 5}
- Lookup x -> 5
- Compute 5 + 3 -> 8
- Store y -> {"x": 5, "y": 8}

---

## Undefined Variables

Using a variable before assignment is an error.

```
print x
```

Error:

```
ValueError: Unknown identifier: x
```

Variables must be assigned before use.

---

## Print Statements

Syntax:

```
print <expression>
```

Evaluation:
1. Evaluate the expression
2. Convert result to string
3. Output the string
4. Return None

---

## Print Example

Program:

```
x = 10
print x
print x + 5
```

Output:

```
10
15
```

---

## Reassignment

Variables can be updated.

```
x = 5
print x
x = 10
print x
```

Output:

```
5
10
```

The binding for `x` is replaced.

---

## Grammar Summary

```
program         = statement_list
statement_list  = [ statement { ";" statement } ]
statement       = print_statement | assignment
assignment      = identifier "=" expression
print_statement = "print" expression
```

Expressions are unchanged from Topic 01.

---

## AST Structure for Programs

Program:

```
x = 10
print x + 5
```

AST:

```
program
├── assign
│   └── target: x
│   └── expression: 10
└── print
    └── expression: x + 5
```

The program node contains a list of statements.

---

## Evaluator: Assignment

```
elif ast["tag"] == "assign":
    value = evaluate(ast["expression"], env)
    env[ast["target"]] = value
    return None
```

Evaluate right side.
Store in environment.

---

## Evaluator: Identifier

```
elif ast["tag"] == "identifier":
    identifier = ast["value"]
    if identifier in env:
        return env[identifier]
    raise ValueError(f"Unknown identifier: {identifier}")
```

Look up variable in environment.

---

## Evaluator: Print

```
elif ast["tag"] == "print":
    value = evaluate(ast["expression"], env)
    print(value)
    return None
```

Evaluate expression.
Output result.

---

## Evaluator: Program

```
elif ast["tag"] == "program":
    for statement in ast["statements"]:
        evaluate(statement, env)
    return None
```

Execute statements sequentially.

---

## Full Pipeline: Tokenize

Input:

```
x = 5; print x * 2
```

Tokens:

```
identifier(x), =, number(5), ;, print, identifier(x), *, number(2)
```

---

## Full Pipeline: Parse

Tokens -> AST:

```
program
├── assign
│   └── target: x
│   └── expression: 5
└── print: 
    └── expression: x * 2
```

---

## Full Pipeline: Evaluate

Initial environment:

```
{}
```

Execute `x = 5`:

```
{"x": 5}
```

Execute `print x * 2`:
```
- Lookup x -> 5
- Compute 5 * 2 -> 10
- Output 10
```
Output:

```
10
```

---

## Execution Model (Current Rules)

- One environment
- All variables live in it
- Execution is sequential
- No nested scopes
- No functions yet

---

## Summary

- Expressions compute values
- Statements perform actions
- Programs are sequences of statements
- Environments store variable bindings
- Evaluation proceeds in order
- Statements return None

Pipeline:

Tokenizer -> Parser -> Evaluator -> Output

---

## Next Steps

- Conditional statements (if)
- Loops (while)
- Nested scopes
- Functions
- More data types