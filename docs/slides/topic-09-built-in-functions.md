# Topic 09: Built-in Functions

`head()`, `tail()`, and `length()` are ordinary-looking calls with special runtime handling.

These built-ins matter because topic 10 uses them to process lists functionally.

---

## What Changes

- Built-in function names
- Runtime dispatch for built-ins
- List helpers: `head()`, `tail()`, `length()`
- A bridge into functional programming

---

## The Main Idea

These are not parser features.

The parser already accepts function calls:

```text
head([1,2,3])
tail([1,2,3])
length([1,2,3])
```

The evaluator decides that certain names are built-ins.

---

## Built-in Names

From the evaluator:

```python
__builtin_functions = ["head", "tail", "length", "keys", "input"]
```

That list tells the runtime which identifiers should become built-in call targets.

---

## Identifier Lookup

When the evaluator sees an identifier, it checks:

```python
if identifier in environment:
    return environment[identifier], None
if "$parent" in environment:
    return evaluate(ast, environment["$parent"])
if identifier in __builtin_functions:
    return {"tag": "builtin", "name": identifier}, None
```

So built-ins are resolved only after normal scope lookup fails.

---

## Built-in Dispatch

Later, call evaluation checks for that special builtin tag:

```python
if function.get("tag") == "builtin":
    return evaluate_builtin_function(function["name"], argument_values)
```

That is the switch that sends `head()` and friends to custom runtime logic.

---

## Head And Tail

From the builtin implementation:

```python
if function_name == "head":
    return (args[0][0] if args[0] else None), None

if function_name == "tail":
    return args[0][1:], None
```

These are simple list operations:

- `head([1,2,3])` -> `1`
- `tail([1,2,3])` -> `[2,3]`

---

## Length

`length()` is the general-purpose one:

```python
if function_name == "length":
    return len(args[0]), None
```

It works on:

- lists
- strings
- objects

---

## Why This Matters

Built-ins show a useful runtime pattern:

- syntax stays ordinary
- names are resolved at evaluation time
- special values are dispatched by the evaluator

And for topic 10, the important part is:

- `head()` and `tail()` let recursive functions inspect and shrink a list
- `length()` gives another example of a built-in value-producing helper

This lets the language add common helpers without giving the parser special cases for each one.
