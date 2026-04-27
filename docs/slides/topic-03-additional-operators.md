# Additional Operators

Comparison and logical operators for richer expressions.

---

## From Topic 02

Topic 02:
- Variables
- Assignment
- Print statements
- Environments

Topic 03:
- Comparison operators
- Logical operators
- Boolean values
- Operator precedence

---

## Comparison Operators

Compare numeric values:

| Operator | Meaning |
| --- | --- |
| `==` | Equal |
| `!=` | Not equal |
| `<` | Less than |
| `<=` | Less than or equal |
| `>` | Greater than |
| `>=` | Greater than or equal |

---

## Comparison Examples

```text
3 == 3     -> true
3 != 3     -> false
3 < 5      -> true
5 <= 5     -> true
10 > 5     -> true
10 >= 10   -> true
```

---

## Boolean Literals

Two special values represent truth and falsity:

```text
true
false
```

Examples:

```text
x = true
y = false
print x
```

---

## Logical AND

Both conditions must be true.

```text
3 < 5 and 5 < 10   -> true
3 < 5 and 5 < 3    -> false
```

---

## Logical OR

At least one condition must be true.

```text
3 > 5 or 5 < 10   -> true
3 > 5 or 5 > 10   -> false
```

---

## Logical NOT

Reverses the truth value.

```text
not true    -> false
not false   -> true
not (3 < 5) -> false
```

---

## Truth and Falsehood

Booleans:
- `true` is truthy
- `false` is falsy

Numbers:
- `0` and `0.0` are falsy
- Any other number is truthy

---

## Type Safety

In logical operations, only booleans and numbers have truth values.

```text
true and 42    -> true
false or 0     -> false
```

Strings, lists, and other types raise an error in boolean context.

---

## Operator Precedence

Lowest to highest:

1. `or`
2. `and`
3. `not`
4. Comparison operators (`==`, `!=`, `<`, etc.)
5. Arithmetic (`+`, `-`)
6. Multiplication and division (`*`, `/`)
7. Unary negation `-`

---

## Precedence Examples

```text
3 < 5 and 5 < 10
= (3 < 5) and (5 < 10)
= true and true
= true
```

---

## Mixed Operators

```text
not 3 < 5
= not (3 < 5)
= not true
= false
```

---

## Short-Circuit Evaluation

- For `and`: if the left side is false, do not evaluate the right side
- For `or`: if the left side is true, do not evaluate the right side

Why it matters:

- efficiency
- safety

---

## Short-Circuit Example: AND

```text
false and (1 / 0)
```

Does not divide by zero.

Evaluates only the left side and returns `false`.

---

## Short-Circuit Example: OR

```text
true or (1 / 0)
```

Does not divide by zero.

Evaluates only the left side and returns `true`.

---

## Unary Minus Recap

Negates a number:

```text
-5     -> -5
--5    -> 5
-(2+3) -> -5
```

Works with any expression.

---

## EBNF Grammar

```text
expression = logic_or
logic_or   = logic_and { "or" logic_and }
logic_and  = logic_not { "and" logic_not }
logic_not  = [ "not" ] comparison
comparison = arithmetic_expression [ compare_op arithmetic_expression ]
compare_op = "==" | "!=" | "<" | "<=" | ">" | ">="
arithmetic_expression = term { ("+" | "-") term }
term       = unary { ("*" | "/") unary }
unary      = { "-" } factor
factor     = number | identifier | boolean | "(" expression ")"
```

---

## Summary

- Comparison operators: `==`, `!=`, `<`, `<=`, `>`, `>=`
- Logical operators: `and`, `or`, `not`
- Boolean literals: `true`, `false`
- Precedence: `or` < `and` < `not` < comparisons < arithmetic
- Short-circuit evaluation for logical expressions

---

## Next Steps

- Conditional statements (`if` / `else`)
- Repetition with `while`
- Block statements
- Statement lists in braces
