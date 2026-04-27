# Control Structures

Adding branching and loops to build real program flow.

---

## From Topic 03

Topic 03:
- Arithmetic, comparison, and logical expressions
- Boolean values
- Operator precedence

Topic 04:
- Conditional execution with `if` / `else`
- Repetition with `while`
- Block statements with `{ ... }`

---

## Why Control Structures?

Without control flow, every statement runs once in order.

Control structures let programs:

- Choose between alternatives
- Repeat work until a condition changes

---

## Statements vs Expressions

Expressions compute values.

Statements perform actions.

Control structures are statements because they change how execution flows.

---

## If Statement

Syntax:

```text
if (<expression>) {
    <statement_list>
}
```

The block executes only when the condition is truthy.

---

## If-Else Statement

Syntax:

```text
if (<expression>) {
    <then_block>
} else {
    <else_block>
}
```

Exactly one block runs.

---

## If Examples

```text
x = 10
if (x > 5) {
    print 1
}

if (x < 5) {
    print 1
} else {
    print 2
}
```

---

## While Statement

Syntax:

```text
while (<expression>) {
    <statement_list>
}
```

Execution repeats while the condition is truthy.

---

## While Example

```text
x = 0
while (x < 3) {
    print x
    x = x + 1
}
```

Output:

```text
0
1
2
```

---

## Block Statements

Blocks group multiple statements:

```text
{
    s1;
    s2;
    s3
}
```

Semicolons are optional at the end and multiple `;` are accepted between statements.

---

## Truthiness Rules

Conditions in `if` and `while` use Topic 03 truthiness:

- `true` is truthy
- `false` is falsy
- `0` and `0.0` are falsy
- Non-zero numbers are truthy

Other value types in boolean context are runtime errors.

---

## Evaluation: If

What it does:

1. Evaluate condition
2. Convert to truth value
3. If truthy, evaluate `then_block`
4. Else evaluate `else_block` if present

Result of an `if` statement is `None`.

---

## Evaluation: While

What it does:

1. Evaluate condition
2. If falsy, stop loop
3. If truthy, evaluate body block
4. Repeat from step 1

Result of a `while` statement is `None`.

---

## AST Shape: If

```text
{
  "tag": "if",
  "condition": ...,
  "then_block": { "tag": "statement_list", ... },
  "else_block": { "tag": "statement_list", ... }   // optional
}
```

---

## AST Shape: While

```text
{
  "tag": "while",
  "condition": ...,
  "do_block": { "tag": "statement_list", ... }
}
```

---

## Parsing Integration

`statement` now includes:

```text
statement =
    print_statement
  | if_statement
  | while_statement
  | assignment_statement
```

This is the parser change that adds `if` and `while`.

---

## Full Grammar (Topic 04)

```text
program         = statement_list
statement_list  = { ";" } [ statement { ";" { ";" } statement } ] { ";" }
print_statement = "print" expression
if_statement    = "if" "(" expression ")" "{" statement_list "}"
                  [ "else" "{" statement_list "}" ]
while_statement = "while" "(" expression ")" "{" statement_list "}"
assignment_statement = identifier "=" expression
statement       = print_statement | if_statement | while_statement | assignment_statement

expression      = logic_or
logic_or        = logic_and { "or" logic_and }
logic_and       = logic_not { "and" logic_not }
logic_not       = [ "not" ] comparison
comparison      = arithmetic_expression [ compare_op arithmetic_expression ]
compare_op      = "==" | "!=" | "<" | "<=" | ">" | ">="
arithmetic_expression = term { ("+" | "-") term }
term            = unary { ("*" | "/") unary }
unary           = { "-" } factor
factor          = number | identifier | "(" expression ")" | "true" | "false"
```

---

## End-to-End Example

```text
x = 5
y = 0

if (x > 0) {
    while (x > 0) {
        y = y + x
        x = x - 1
    }
} else {
    y = -1
}

print y
```

This combines comparison, logic, `if`, and `while` in one program.

---

## Next Steps

- Function expressions
- Function calls
- Function statements as sugar
- Environments for nested execution
