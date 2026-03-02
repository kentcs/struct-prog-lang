# Simple Expressions

A short deck about literals, operators, and precedence.

---

## What We're Building

A complete interpreter for PMDAS expressions.

```
2 + 3 * 4 - (5 / 2)
```

Pipeline: **Tokenizer** → **Parser** → **Evaluator** → **Result**

---

## Goals

- Identify expression forms
- Evaluate expressions step by step
- Explain precedence and associativity

---

## Literals

- Numbers: `1`, `2.5`
- Strings: `"hi"`
- Booleans: `true`, `false`

---

## Operators

| Type | Examples |
| --- | --- |
| Arithmetic | `+ - * /` |
| Comparison | `== != < <= > >=` |
| Logical | `and or not` |

---

## The Tokenizer (aka Lexer or Scanner)

Converts raw text into a stream of tokens.

---

## What the Tokenizer Recognizes

- Numbers: integers and floats
- Operators: `+`, `-`, `*`, `/`, `%`
- Parentheses: `(`, `)`
- Whitespace and comments (skipped)

---

## Regex (for tokenization)

- Matches local patterns in `tokenizer.py` (whitespace, numbers, operators)
- Scans left-to-right and chooses the first matching pattern
- Cannot verify balanced structure like `((1 + 2) * 3)`

---

## Tokenizer (module)

- `tokenizer.py` converts text into tokens with `tag`, `line`, `column`
- Uses regex rules for `number`, `+ - * / ( )`, and `whitespace`
- Skips whitespace, raises on unexpected characters
- Appends an end token with `tag: None` for parser lookahead

---

## Tokenizer Output

A sequence of tokens with metadata:

```json
[
  {tag: "number", value: 2, line: 1, column: 1},
  {tag: "+", line: 1, column: 3},
  {tag: "number", value: 3, line: 1, column: 5},
  {tag: "*", line: 1, column: 7},
  {tag: "number", value: 4, line: 1, column: 9},
  {tag: null}
]
```

---

## EBNF (for grammar)

- Describes how tokens form valid expressions
- Uses recursion to model nesting and precedence
- Can express balanced parentheses, e.g. `"(" expr ")"`
- Unlike regex, EBNF can enforce balanced structures

---

## Parser Strategy

Uses recursive descent parsing:

```
expression = term { ("+" | "-") term }
term       = factor { ("*" | "/" | "%") factor }
factor     = number | "(" expression ")"
```

---

## Precedence Guarantee

The grammar automatically ensures:

- `2 + 3 * 4` → `2 + (3 * 4)` ✓
- `(2 + 3) * 4` → `(2 + 3) * 4` ✓

---

## Parser (module)

- `parser.py` implements the recursive descent strategy above
- Produces AST nodes like `{tag: "+", left: ..., right: ...}`
- Currently accepts numbers and operators with full parenthesis support

---

## What the Parser Does

- Respects operator precedence
- Handles parentheses
- Structures data into a tree

---

## EBNF from the code

```text
expression = term { ("+" | "-") term }
term       = factor { ("*" | "/" | "%") factor }
factor     = <number> | "(" expression ")"
```

---

## Token to AST (example)

Input:

`3*4+5`

Tokens:

```text
[3] [*] [4] [+] [5]
```

AST:

```text
        +
     / \
    *   5
 / \
3   4
```

---

## AST as JSON (example)

```json
{
    "tag": "+",
    "left": {
        "tag": "*",
        "left": {"tag": "number", "value": 3},
        "right": {"tag": "number", "value": 4}
    },
    "right": {"tag": "number", "value": 5}
}
```

---

## Precedence

`*` and `/` bind tighter than `+` and `-`.

```text
1 + 2 * 3 = 7
(1 + 2) * 3 = 9
```

---

## Associativity

Left-associative operators group left-to-right.

```text
10 - 3 - 2 = (10 - 3) - 2
```

---

## Parse Tree (Sketch)

```
    -
   / \
  -   2
 / \
10  3
```

---

## The Evaluator

Traverses the AST and computes the result.

---

## How Evaluation Works

1. Recursively evaluate each node
2. Apply operators in tree order
3. Return final numeric value

---

## Evaluator Example

```
AST:     +
        / \
       2   *
          / \
         3   4
```

Steps: `2 + (3 * 4) = 2 + 12 = 14`

---

## The Runner

Orchestrates the full pipeline.

---

## Runner Steps

1. Take source code as input
2. Call tokenizer
3. Call parser
4. Call evaluator
5. Return result

---

## Runner Example

```
runner("2 + 3 * 4")
  ↓
Tokenize
  ↓
Parse
  ↓
Evaluate
  ↓
14
```

---

## Full Pipeline Example

Input: `2 + 3 * (4 - 1)`

---

## Tokenizer Output

```
2, +, 3, *, (, 4, -, 1, )
```

---

## Parser Output

```
        +
       / \
      2   *
         / \
        3   -
           / \
          4   1
```

---

## Evaluator Output

```
Eval(-): 4 - 1 = 3
Eval(*): 3 * 3 = 9
Eval(+): 2 + 9 = 11

Result: 11
```

---

## Quick Check

Evaluate:

`4 + 5 * 2`

---

## Answer

`14`

---

## Component Interaction

```
Source Code → Tokenizer → Parser → Evaluator → Result
```

Each component:
- Does one thing
- Passes clean data to the next

---

## Why This Architecture?

- Separation of concerns
- Testability
- Clarity
- Extensibility

---

## This Pattern Everywhere

Python, JavaScript, Go, Java, C...

Any language uses this same pipeline structure.

