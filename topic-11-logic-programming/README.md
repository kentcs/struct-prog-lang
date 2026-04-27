# Topic 11: Logic Programming

This folder holds a small set of GNU Prolog examples for this topic.

The point is not to build a Prolog interpreter. The point is to see a different programming model:

- facts
- rules
- queries
- unification
- backtracking

## Files

- `family.pl`: simple family facts and derived relations
- `lists.pl`: small list-processing examples
- `sort.pl`: quicksort in Prolog
- `unification.pl`: simple unification examples

## Installing GNU Prolog

Common install options:

- macOS with Homebrew:

```bash
brew install gnu-prolog
```

- Ubuntu or Debian:

```bash
sudo apt install gprolog
```

After installation, start the Prolog prompt with:

```bash
gprolog
```

## Basic Usage

At the GNU Prolog prompt, load a file with `consult/1`:

```prolog
?- consult('family.pl').
```

You can also use the bracket shorthand:

```prolog
?- ['family.pl'].
```

Ask questions by writing queries:

```prolog
?- child(greg, david).
?- grandchild(X, jack).
?- sibling(kim, steph).
```

Some useful habits:

- variables start with uppercase letters: `X`, `Y`, `Person`
- atoms usually start with lowercase letters: `greg`, `jack`, `daughter`
- end each query with a period
- type `;` after an answer to ask for another solution
- type `halt.` to leave GNU Prolog

## Suggested Sequence To Try

Start with facts and simple rules:

```prolog
?- consult('family.pl').
?- son(greg, david).
?- child(greg, david).
?- grandchild(X, jack).
```

Then try list structure and pattern matching:

```prolog
?- consult('lists.pl').
?- first([a,b,c], X).
?- rest([a,b,c], X).
?- member2(c, [a,b,c,d]).
```

Then try unification:

```prolog
?- consult('unification.pl').
?- X = greg.
?- point(X, 2) = point(1, Y).
?- [H|T] = [a,b,c].
?- likes(Person, pizza).
```

Then finish with sorting:

```prolog
?- consult('sort.pl').
?- qsort([5,3,7,2,5,1], X).
```

## Main Ideas

Two ideas matter most at the start:

1. Think in terms of relations, not step-by-step commands.
2. Remember that Prolog searches for values that make the query true.

That is the main shift. Once that part is clear, the rest of the syntax makes a lot more sense.

## Better Unification Examples

For a clear view of unification, try these in this order:

```prolog
?- X = greg.
?- X = Y.
?- point(X, 2) = point(1, Y).
?- [H|T] = [a,b,c].
?- point(X, 2) = line(1, 2).
```

What each one shows:

- `X = greg.` binds a variable to an atom.
- `X = Y.` shows that two unbound variables can unify.
- `point(X, 2) = point(1, Y).` shows field-by-field matching inside a structure.
- `[H|T] = [a,b,c].` shows head/tail matching on a list.
- `point(X, 2) = line(1, 2).` fails because the term shapes do not match.

That sequence usually makes the idea much clearer.
