# Functions

Function calls, parameters, and environments.

---

## What This Topic Adds

- Function expressions
- Function calls
- Parameter binding
- Dynamic binding
- Static binding

---

## Big Idea

Functions are values.

They can be:

- stored in variables
- passed around
- called like expressions

---

## From Topic 04

Topic 04 gave us:

- `if`
- `while`
- blocks

Topic 05 adds functions on top of that model.

---

## Function Expression

```text
function(x, y) {
    print x + y
}
```

This creates a function object.

---

## Storing A Function

```text
add = function(x, y) {
    print x + y
}
```

`add` now refers to a function value.

---

## Calling A Function

```text
f(1, 2)
```

Calls are expressions.

---

## Parameters And Arguments

- Parameters are the names in the function definition
- Arguments are the values at the call site

Example:

```text
function(x) { print x }
```

Called as:

```text
f(2)
```

---

## Call Steps

When evaluating `f(1, 2)`:

1. Evaluate `f`
2. Evaluate the arguments
3. Bind parameters
4. Execute the body

---

## Parameter Binding

Call:

```text
add(3, 4)
```

Local environment:

```text
{
  "x": 3,
  "y": 4
}
```

---

## Dynamic Binding

Dynamic binding means:

```text
local_environment["$PARENT"] = environment
```

The function body sees the **calling environment** next.

---

## Dynamic Binding Example

```text
x = 3;
f = function() {
    print x
};
g = function() {
    x = 4;
    f()
};
g();
```

With dynamic binding, `f()` sees `x = 4` from the call inside `g()`.

---

## Static Binding

Static binding means:

```text
local_environment["$PARENT"] = function["environment"]
```

The function body sees the **definition environment** next.

---

## Static Binding Example

```text
x = 3;
f = function() {
    print x
};
g = function() {
    x = 4;
    f()
};
g();
```

With static binding, `f()` sees `x = 3` from where `f` was defined.

---

## Function-Statement Sugar

The parser also accepts:

```text
function f(x) {
    statements
}
```

This is rewritten into:

```text
f = function(x) {
    statements
}
```

---

## Why Sugar Helps

One runtime form is enough:

- assignment to a name
- function expression on the right-hand side

The sugar keeps the source readable.

---

## Return Later

We have not implemented `return` yet.

So for now:

- function bodies run for effects
- calls evaluate to `None`
- `return` is a later lecture

---

## Evaluator Changes

The evaluator now:

- Returns a function object for `function`
- Evaluates call arguments first
- Binds parameters in a fresh local environment
- Uses the captured defining environment for static binding

---

## Example: Identity Function

```text
id = function(x) { print x; }
id(42)
```

Execution:

1. Bind `id` to a function object
2. Call `id(42)`
3. Create a local environment with `x = 42`
4. Execute the body in that environment

---

## Example: Higher-Order Function

```text
apply = function(f, x) { print f(x); }
id = function(x) { x }
apply(id, 42)
```

The function `apply` takes another function as an argument.

---

## What We Have Not Added Yet

We have not implemented `return` statements yet.

So at this stage:

- function bodies run for effects
- calls currently evaluate to `None`
- returning a specific value is a later feature

---

## Why That Matters

`return` changes:

- parser rules
- evaluator control flow
- how function calls produce values

That is separate from function creation and binding.

---

## Next Steps

- `return` statements
- early return from function bodies
- function call results
- more complete function examples
