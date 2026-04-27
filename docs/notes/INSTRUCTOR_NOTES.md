# Topic 11 Instructor Notes

This file is for lecture prep. It is not meant for students.

## Main Goals

Students should leave this topic with four basic ideas:

1. A Prolog program is a set of facts and rules.
2. A query asks whether some relationship can be made true.
3. Variables are solved by unification.
4. Prolog searches for answers by backtracking.

Do not try to teach all of Prolog in one shot. That always ends badly.

## Suggested Flow

### 1. Start with facts

Load `family.pl` and ask plain yes/no questions:

```prolog
?- consult('family.pl').
?- son(greg, david).
?- daughter(kim, david).
```

Then switch to variables:

```prolog
?- child(X, david).
?- grandchild(X, jack).
```

This is usually the first useful moment. Students see that the query is not a function call. It is a search for bindings that make the statement true.

### 2. Show a rule

Use:

```prolog
child(X, Y) :- son(X, Y).
child(X, Y) :- daughter(X, Y).
```

Explain `:-` in plain language:

- left side: what we want to prove
- right side: what must be true for that to work

Keep the explanation conversational. If you sound like a logic textbook, you lose half the room.

### 3. Show unification directly

Load `unification.pl` and do a few small examples:

```prolog
?- X = greg.
?- X = Y.
?- point(X, 2) = point(1, Y).
?- [H|T] = [a,b,c].
?- point(X, 2) = line(1, 2).
```

Walk through them in this order:

1. `X = greg.` means a variable can be bound to a value.
2. `X = Y.` means two unbound variables can unify.
3. `point(X, 2) = point(1, Y).` means matching happens field by field.
4. `[H|T] = [a,b,c].` means list structure can be matched the same way.
5. `point(X, 2) = line(1, 2).` fails because the outer shapes differ.

The point is that Prolog matches term shapes and fills in variables as it goes.

### 4. Show backtracking

Use:

```prolog
?- likes(Person, pizza).
```

Then press `;` for another answer.

That is the cleanest way to show that Prolog keeps searching after the first solution.

### 5. End with recursion over lists

Use `lists.pl` first, then `sort.pl`.

Suggested order:

```prolog
?- consult('lists.pl').
?- member2(c, [a,b,c,d]).
?- append2([1,2], [3,4], X).
?- length2([a,b,c], N).
```

Then:

```prolog
?- consult('sort.pl').
?- qsort([5,3,7,2,5,1], X).
```

This gives a good bridge back to the course because students have already seen recursive list processing in other languages.

## Things To Emphasize

- Prolog is declarative. You describe relationships more than control flow.
- Order still matters more than students expect.
- Variables in a query are not mutable variables in the usual sense.
- Unification is not the same thing as assignment.
- Backtracking is part of the execution model, not a special debugging mode.

## Things That Usually Confuse Students

- Uppercase means variable, lowercase means atom.
- `=` is unification, not arithmetic comparison.
- `is` is for arithmetic evaluation.
- `X = Y + 1` is not the same as `X is Y + 1`.
- A failed query is just `no`. It is not necessarily a crash.
- Term shape matters. Matching `point(...)` with `line(...)` fails even if the inside values look similar.

## Good Live Queries

These usually work well on the board:

```prolog
?- child(X, david).
?- sibling(kim, X).
?- point(X, 2) = point(1, Y).
?- [H|T] = [a,b,c].
?- append2([1,2], [3,4], X).
?- qsort([4,1,6,2], X).
```

## What Not To Overdo

- do not start with operator precedence or the full Prolog standard library
- do not spend too long on installation during class
- do not pretend Prolog is just "functions written funny"
- do not try to cover cuts, negation, or meta-programming here unless the class is unusually comfortable

## Short Contrast With Trivial

Useful one-liner:

> In Trivial, we tell the machine what steps to carry out. In Prolog, we describe a relationship and ask the machine to find values that make it true.

That contrast is the point of the topic.
