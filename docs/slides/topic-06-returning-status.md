# Returning Status

Return, break, continue, and exit need more than a plain value.

---

## What This Topic Adds

- `return`
- `break`
- `continue`
- `exit`
- Status-aware evaluation

---

## The Problem

Some statements do not just produce a value.

They change control flow:

- leave a function
- leave a loop
- stop the program

---

## Example: `return`

```text
f = function() {
    return 7
};
print f()
```

`return` should stop the function body immediately.

---

## The New Shape

Evaluation now returns:

```text
value, status
```

Normal completion uses:

```text
value, None
```

---

## What Propagates

Most expression nodes do not invent a status.

They either:

- return a normal value
- or pass along a special status from a child node

That is the key rule for expressions.

---

## Return

`return` exits a function early.

Example:

```text
return 42
```

Status:

```text
"return"
```

---

## Example: `break`

```text
x = 0;
while (true) {
    x = x + 1;
    if (x == 3) {
        break
    }
};
print x
```

`break` should stop the loop, not the whole program.

---

## Break

`break` exits the nearest loop.

Example:

```text
break
```

Status:

```text
"break"
```

---

## Example: `continue`

```text
i = 0;
while (i < 5) {
    i = i + 1;
    if (i % 2 == 0) {
        continue
    }
    print i
}
```

`continue` skips the rest of the loop body.

---

## Continue

`continue` skips to the next loop iteration.

Example:

```text
continue
```

Status:

```text
"continue"
```

---

## Example: `exit`

```text
print 1;
exit 0;
print 2
```

`exit` should stop the whole program immediately.

---

## Exit

`exit` stops the program.

Example:

```text
exit 0
```

Status:

```text
"exit"
```

---

## Who Clears Status?

Some nodes consume special statuses and turn them back into normal completion.

Examples:

- `function` consumes `return`
- `while` consumes `break` and `continue`
- `program` may consume `exit` at the top level

---

## Who Propagates Status?

Most expression nodes do not clear status.

They just forward it upward:

- arithmetic
- comparisons
- logical operators
- list indexing
- list construction

If a child returns `"return"`, the parent must not ignore it.

---

## Why Status Matters

Without status propagation:

- nested calls swallow `return`
- loops ignore `break`
- loops ignore `continue`
- programs cannot stop cleanly

---

## Function Calls

Function calls must:

- evaluate arguments
- bind parameters
- run the body
- consume `return`

That is how call results are produced.

Example:

```text
f = function(x) {
    return x + 1
};
print f(4)
```

---

## While Loops

`while` is a status-aware control node.

It should:

- evaluate the condition
- run the body
- stop on `break`
- repeat on `continue`
- propagate `return` and `exit`

That is why loops are different from plain expressions.

---

## Propagation Rule

Each evaluator step should do this:

1. Evaluate child nodes
2. Check the status
3. Propagate special statuses upward
4. Only continue normally when status is `None`

---

## Next Step

With status in place, we can implement:

- early return
- loop control
- program exit
- cleaner function results

---

## Open Question

How would an `"exception"` status propagate?

What kind of thing would handle that status?

---

## Hint

Think about a construct that:

- runs a block of code
- watches for a special status
- stops normal propagation when it sees one

It would be a kind of boundary, not a regular expression.
