# Simple Expressions

A short deck about literals, operators, and precedence.

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

## EBNF (for grammar)

- Describes how tokens form valid expressions
- Uses recursion to model nesting and precedence
- Can express balanced parentheses, e.g. `"(" expr ")"`
- Unlike regex, EBNF can enforce balanced structures

---

## Parser (module)

- `parser.py` implements:
    - `factor = <number>`
    - `term = factor { ("*" | "/") factor }`
    - `expression = term { ("+" | "-") term }`
- Produces AST nodes like `{tag: "+", left: ..., right: ...}`
- Currently accepts numbers and operators only (no parentheses yet)

---

## EBNF from the code

```text
expression = term { ("+" | "-") term }
term       = factor { ("*" | "/") factor }
factor     = <number>
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

## Quick Check

Evaluate:

`4 + 5 * 2`

---

## Answer

`14`

---

## Thanks!

Questions?
