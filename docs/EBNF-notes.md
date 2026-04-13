# Introduction to EBNF

This document introduces Extended Backus-Naur Form (EBNF) as a practical tool for describing the structure of programming languages and data formats. It is written for students who will soon implement tokenizers and parsers.

---

## 1. What a Grammar Is

A grammar is a formal description of the structure of a language.

- It defines what strings are valid in the language.
- It does not execute code or compute values.
- It answers the question: "What does a well-formed program look like?"

Examples of things a grammar can describe:

- Arithmetic expressions
- A subset of JavaScript
- A configuration file format
- A simple command language

Informal example (English-like):

- An expression is a term followed by zero or more "+ term" parts.

EBNF lets us write this precisely.

---

## 2. The Idea Behind BNF and EBNF

BNF (Backus-Naur Form) was created to describe programming languages.

EBNF is a small extension that adds conveniences:

- Repetition
- Optional parts
- Grouping

EBNF is not one single standard. Many dialects exist, but the core ideas are consistent.

We will use a simple, readable form.

---

## 3. Basic Notation

An EBNF rule has the form:

```
name ::= definition
```

- `name` is a nonterminal (a grammatical category)
- `definition` is built from other nonterminals and terminals

Terminals are literal tokens or symbols, often written in quotes.

Example:

```
number ::= digit { digit }
digit  ::= "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"
```

This says:

- A `number` is a `digit` followed by zero or more `digit`s.

---

## 4. Core Operators

We will use these operators:

- `|`   choice (alternation)
- `{ }` repetition (zero or more)
- `[ ]` optional (zero or one)
- `( )` grouping

Examples:

```
sign ::= "+" | "-"

integer ::= [ sign ] digit { digit }
```

This allows:

- `7`
- `-3`
- `+42`

But not:

- `--3`
- `+`

---

## 5. Describing Expressions

A simple arithmetic grammar:

```
expression ::= term { ("+" | "-") term }
term       ::= factor { ("*" | "/") factor }
factor     ::= number | "(" expression ")"
number     ::= digit { digit }
digit      ::= "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"
```

This encodes precedence:

- `*` and `/` bind tighter than `+` and `-`
- Parentheses override everything

Valid strings:

- `3+4`
- `2*(5+1)`
- `10/2-3`

Invalid strings:

- `+3`
- `3+`
- `2*(4+`

---

## 6. Tokens vs Grammar

In practice, grammars usually operate on tokens, not characters.

Instead of:

```
number ::= digit { digit }
```

We often assume:

```
number ::= <NUMBER>
identifier ::= <IDENTIFIER>
```

Where `<NUMBER>` and `<IDENTIFIER>` are produced by a tokenizer.

This keeps the grammar focused on structure, not spelling.

Example:

```
assignment ::= identifier "=" expression
```

---

## 7. Statements and Blocks

A tiny statement language:

```
program   ::= { statement }

statement ::= assignment ";"
            | "if" "(" expression ")" block
            | "while" "(" expression ")" block

assignment ::= identifier "=" expression

block ::= "{" { statement } "}"
```

This allows programs like:

```
x = 3;
while (x) {
    x = x - 1;
}
```

---

## 8. What Grammars Do Not Do

A grammar does not:

- Check types
- Evaluate expressions
- Enforce variable declaration rules
- Decide whether a variable exists

For example, the grammar can allow:

```
x = y + 3;
```

Even if `y` is undefined. That is the interpreter's or compiler's job.

Grammar answers only:

- Is this structurally valid?

---

## 9. Ambiguity

A grammar is ambiguous if a string can be parsed in more than one way.

Classic example:

```
expression ::= expression "+" expression | number
```

The string:

```
1 + 2 + 3
```

Can be grouped as:

- `(1 + 2) + 3`
- `1 + (2 + 3)`

We remove ambiguity by introducing structure (term, factor, etc.).

---

## 10. Why EBNF Matters

EBNF is the bridge between:

- Informal language descriptions
- Working parsers

It lets us:

- Be precise
- Communicate structure
- Generate or implement parsers
- Reason about edge cases

In this course, EBNF will be:

- The contract between the language design and the parser
- The blueprint for recursive descent functions

Each nonterminal becomes a function.
Each rule becomes code.

---

## 11. From Rule to Code (Preview)

Given:

```
expression ::= term { ("+" | "-") term }
```

We will eventually write something like:

```
def parse_arithmetic_term(tokens):
    """
    arithmetic_term ::= arithmetic_factor { ("*" | "/") arithmetic_factor }
    """
    node, tokens = parse_arithmetic_factor(tokens)
    while tokens[0]["tag"] in ["*", "/", "%"]:
        tag = tokens[0]["tag"]
        next_node, tokens = parse_arithmetic_factor(tokens[1:])
        node = {"tag": tag, "left": node, "right": next_node}
    return node, tokens
```

EBNF is not abstract theory. It is executable design.