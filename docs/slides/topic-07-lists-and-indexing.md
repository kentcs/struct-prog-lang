# Lists and Indexing

Assignment grows from names to list elements.

---

## What This Topic Adds

- Assignment expressions
- List literals
- Indexing
- List element assignment

---

## The Assignment Model

The grammar now treats assignment as an expression:

```text
assignment_expression = [ "extern" ] logical_expression [ "=" assignment_expression ]
expression = assignment_expression
statement = ... | expression
```

That means an assignment can appear where a statement is expected.

---

## Assignment As A Statement

Trivial code can use assignment directly as a statement:

```text
x = [1,2,3];
x[1] = 27;
```

Because `statement` accepts `expression`, the parser does not need a
special “assignment statement” rule here.

---

## Parser Shape

The parser handles assignment inside expressions, then lets statements
fall back to expression parsing.

```python
assignment_expression = [ "extern" ] logical_expression [ "=" assignment_expression ]
statement = if_statement | while_statement | function_statement | return_statement | print_statement | exit_statement | import_statement | break_statement | continue_statement | assert_statement | expression
```

So the statement layer stays simple.

---

## List Literals

Trivial list literals look like this:

```text
[1, 2, 3]
[]
[[1,2], [3,4]]
```

The key idea is that a list value can contain many values in order.

---

## List Literal Grammar

In the parser:

```text
list = "[" expression { "," expression } "]"
```

And the implementation is just a loop over comma-separated expressions.

---

## List Creation

The parser turns list syntax into an AST node:

```python
if token["tag"] == "[":
    return parse_list(tokens)
```

Then the evaluator constructs the runtime list value by evaluating each item.

---

## List Evaluation

```python
if ast["tag"] == "list":
    items = []
    for item in ast["items"]:
        result, item_status = evaluate(item, environment)
        items.append(result)
    return items, None
```

That is the bridge from syntax to runtime value.

---

## Indexing

Trivial code uses indexing like this:

```text
x[0]
x[1][0]
```

The parser treats `[` after an expression as indexing, not a new list literal.

---

## Indexing In The Parser

```python
while tokens[0]["tag"] in ["[", ".", "("]:
    if tokens[0]["tag"] == "[":
        tokens = tokens[1:]
        index_ast, tokens = parse_expression(tokens)
        tokens = tokens[1:]  # "]"
        ast = {"tag": "complex", "base": ast, "index": index_ast}
```

That one branch is what makes `x[0]` possible.

---

## List Assignment

Trivial can update a list element:

```text
x = [1,2,3];
x[1] = 27;
```

This is not assignment to a name.

It is assignment through an index into an existing list.

---

## List Assignment In The Evaluator

```python
elif target["tag"] == "complex":
    base, base_status = evaluate(target["base"], environment)
    index, index_status = evaluate(target["index"], environment)
    if isinstance(base, list):
        target_base = base
        target_index = index
```

That path is what mutates the list in place.

---

## The Core Idea

List support forces the language to separate:

- names
- indexes
- values
- mutation

That is the first step from simple expressions toward real data structures.
