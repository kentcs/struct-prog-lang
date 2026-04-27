# Topic 08: Simple Objects

Objects are dictionary-like values.

The core idea is simple:

- object literals build key/value maps
- `x.a` is sugar for `x["a"]`
- object assignment updates existing entries

---

## What Changes

- Object literals
- Dot access as syntactic sugar
- Object lookup and update
- Nested objects

---

## Object Literals

Trivial code:

```text
person = {
    "name": "Alice",
    "age": 30,
    "active": true
};
```

An object literal is just a structured bundle of values.

---

## Object Grammar

From the parser:

```text
object = "{" [ expression ":" expression { "," expression ":" expression } ] "}"
```

That is the same basic pair structure as a Python dict.

---

## Runtime Shape

The evaluator turns objects into dictionaries:

```python
if ast["tag"] == "object":
    object = {}
    for item in ast["items"]:
        key, key_status = evaluate(item["key"], environment)
        value, value_status = evaluate(item["value"], environment)
        object[key] = value
    return object, None
```

So the runtime representation is straightforward.

---

## Dot Access

Trivial code:

```text
person.name
person.age
```

The parser treats `.` as sugar for string-key lookup:

```python
ast = {
    "tag": "complex",
    "base": ast,
    "index": {"tag": "string", "value": tokens[0]["value"]},
}
```

---

## One Node, Many Cases

The same `complex` AST handles:

- `x[0]`
- `x["name"]`
- `x.name`

From the evaluator:

```python
if ast["tag"] == "complex":
    base, _ = evaluate(ast["base"], environment)
    index, _ = evaluate(ast["index"], environment)
```

Then the runtime decides whether `base` is a list or an object.

---

## Object Update

Trivial code:

```text
person["age"] = 31;
person["city"] = "New York";
```

This updates the existing object in place.

---

## Assignment Through An Index

From the evaluator:

```python
elif target["tag"] == "complex":
    base, base_status = evaluate(target["base"], environment)
    index_ast = target["index"]
    ...
    elif isinstance(base, dict):
        target_base = base
        target_index = index
```

That same path also works for `person.age = 31`.

---

## Nested Objects

Trivial code:

```text
company = {
    "employee": {
        "name": "Bob",
        "department": "Engineering"
    }
};
```

Objects can contain other objects, lists, numbers, strings, booleans, and whatever else the language already knows about.

---

## Why It Matters

This topic shows a useful pattern:

- a new data type
- syntax sugar on top of existing indexing
- runtime mutation through the same access path

That is how a simple object system gets started.
